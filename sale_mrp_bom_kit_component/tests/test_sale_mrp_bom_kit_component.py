# Copyright 2026 Eshan Desle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command
from odoo.tests.common import TransactionCase, new_test_user


class TestSaleMrpBomKitComponent(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.warehouse = cls.env.ref("stock.warehouse0")

        # Products
        cls.kit_product = cls.env["product.product"].create(
            {
                "name": "Computer Bundle",
                "type": "consu",
            }
        )
        cls.comp_cpu = cls.env["product.product"].create(
            {
                "name": "CPU",
                "type": "consu",
            }
        )
        cls.comp_ram = cls.env["product.product"].create(
            {
                "name": "RAM 16GB",
                "type": "consu",
            }
        )
        cls.comp_psu = cls.env["product.product"].create(
            {
                "name": "Power Supply",
                "type": "consu",
            }
        )
        cls.std_product = cls.env["product.product"].create(
            {
                "name": "Standard Mouse",
                "type": "consu",
            }
        )

        # Phantom BoM (Kit)
        cls.kit_bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.kit_product.product_tmpl_id.id,
                "product_id": cls.kit_product.id,
                "type": "phantom",
                "product_qty": 1.0,
            }
        )
        cls.bom_line_cpu = cls.env["mrp.bom.line"].create(
            {
                "bom_id": cls.kit_bom.id,
                "product_id": cls.comp_cpu.id,
                "product_qty": 1.0,
                "sequence": 1,
            }
        )
        cls.bom_line_ram = cls.env["mrp.bom.line"].create(
            {
                "bom_id": cls.kit_bom.id,
                "product_id": cls.comp_ram.id,
                "product_qty": 1.0,
                "sequence": 2,
            }
        )
        cls.bom_line_psu = cls.env["mrp.bom.line"].create(
            {
                "bom_id": cls.kit_bom.id,
                "product_id": cls.comp_psu.id,
                "product_qty": 1.0,
                "sequence": 3,
            }
        )

    def _create_sale_order(self):
        return self.env["sale.order"].create({"partner_id": self.partner.id})

    def _create_kit_order_line(self, order, qty=1.0):
        return self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.kit_product.id,
                "product_uom_qty": qty,
                "price_unit": 100.0,
                "bom_id": self.kit_bom.id,
            }
        )

    def test_auto_populate_components(self):
        """AC1: Kit product initializes components from phantom BoM."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order)

        self.assertTrue(line.is_kit)
        self.assertEqual(len(line.kit_component_ids), len(self.kit_bom.bom_line_ids))
        self.assertTrue(all(line.kit_component_ids.mapped("is_selected")))
        self.assertEqual(
            set(line.kit_component_ids.mapped("product_id.id")),
            {self.comp_cpu.id, self.comp_ram.id, self.comp_psu.id},
        )

    def test_deselected_component_excluded_from_delivery(self):
        """AC2: Deselected components are excluded from generated delivery moves."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order)

        # Deselect RAM
        ram_comp = line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_ram
        )
        ram_comp.is_selected = False

        order.action_confirm()

        self.assertEqual(order.state, "sale")
        self.assertTrue(order.picking_ids)
        delivery_products = order.picking_ids.move_ids.mapped("product_id")

        self.assertIn(self.comp_cpu, delivery_products)
        self.assertIn(self.comp_psu, delivery_products)
        self.assertNotIn(self.comp_ram, delivery_products)

    def test_modified_component_quantity(self):
        """AC3: Modifying component qty scales demand in delivery moves."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=2.0)

        # Change Power Supply quantity from 1 to 3
        psu_comp = line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_psu
        )
        psu_comp.product_qty = 3.0

        order.action_confirm()

        psu_move = order.picking_ids.move_ids.filtered(
            lambda m: m.product_id == self.comp_psu
        )
        self.assertTrue(psu_move)
        # 3.0 per kit * 2 kits = 6.0
        self.assertEqual(psu_move.product_uom_qty, 6.0)

    def test_reset_to_default_bom(self):
        """AC4: Resetting components restores original BoM lines and quantities."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order)

        # Customize components: deselect RAM, increase CPU qty
        ram_comp = line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_ram
        )
        ram_comp.is_selected = False
        cpu_comp = line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_cpu
        )
        cpu_comp.product_qty = 5.0

        # Action reset
        line.action_reload_kit_components()

        self.assertEqual(len(line.kit_component_ids), 3)
        self.assertTrue(all(line.kit_component_ids.mapped("is_selected")))
        cpu_comp_reloaded = line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_cpu
        )
        self.assertEqual(cpu_comp_reloaded.product_qty, 1.0)

    def test_non_kit_lines_unaffected(self):
        """AC5: Non-kit sale order lines operate without interference."""
        order = self._create_sale_order()
        std_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.std_product.id,
                "product_uom_qty": 3.0,
                "price_unit": 25.0,
            }
        )
        self.assertFalse(std_line.is_kit)
        self.assertFalse(std_line.kit_component_ids)

        order.action_confirm()
        self.assertEqual(order.state, "sale")
        delivery_products = order.picking_ids.move_ids.mapped("product_id")
        self.assertIn(self.std_product, delivery_products)
        std_move = order.picking_ids.move_ids.filtered(
            lambda m: m.product_id == self.std_product
        )
        self.assertEqual(std_move.product_uom_qty, 3.0)

    def test_multi_company_isolation(self):
        """AC6: Cross-company access rules prevent unauthorized access to components."""
        company_b = self.env["res.company"].create({"name": "Company B"})
        user_b = new_test_user(
            self.env,
            login="user_company_b",
            groups="sales_team.group_sale_salesman",
            company_id=company_b.id,
            company_ids=[company_b.id],
        )

        order_a = self._create_sale_order()
        line_a = self._create_kit_order_line(order_a)
        comp_a = line_a.kit_component_ids[0]

        # User B should not be able to read/write Company A's component lines
        with self.assertRaises(AccessError):
            comp_a.with_user(user_b).read(["product_id"])

    def test_qty_delivered_complete_and_partial(self):
        """Test complete and partial kit delivery and qty_delivered calculation."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=1.0)
        order.action_confirm()

        picking = order.picking_ids
        self.assertEqual(len(picking.move_ids), 3)

        # Partially deliver: only CPU
        cpu_move = picking.move_ids.filtered(lambda m: m.product_id == self.comp_cpu)
        cpu_move.quantity = 1.0
        cpu_move.picked = True
        # Partial kit delivery should result in 0 kit delivered
        line._compute_qty_delivered()
        self.assertEqual(line.qty_delivered, 0.0)

        # Complete delivery for RAM and PSU
        other_moves = picking.move_ids - cpu_move
        for move in other_moves:
            move.quantity = 1.0
            move.picked = True
        picking.button_validate()

        line._compute_qty_delivered()
        self.assertEqual(line.qty_delivered, 1.0)

    def test_qty_delivered_with_deselected_components(self):
        """Test that delivered qty is 1.0 when all selected components are delivered."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=1.0)
        ram_comp = line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_ram
        )
        ram_comp.is_selected = False
        order.action_confirm()

        picking = order.picking_ids
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.button_validate()

        line._compute_qty_delivered()
        self.assertEqual(line.qty_delivered, 1.0)

    def test_all_components_deselected(self):
        """Test behavior when all kit components are deselected."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=1.0)
        line.kit_component_ids.write({"is_selected": False})
        order.action_confirm()

        # No delivery moves generated because all components were excluded
        self.assertFalse(order.picking_ids.move_ids)
        line._compute_qty_delivered()
        self.assertEqual(line.qty_delivered, 0.0)

    def test_multiple_kit_lines_same_picking(self):
        """Test delivery of multiple kit order lines in the same picking."""
        order = self._create_sale_order()
        line1 = self._create_kit_order_line(order, qty=1.0)
        line2 = self._create_kit_order_line(order, qty=2.0)
        # Deselect PSU on line 2
        psu_comp2 = line2.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_psu
        )
        psu_comp2.is_selected = False
        order.action_confirm()

        picking = order.picking_ids
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.button_validate()

        line1._compute_qty_delivered()
        line2._compute_qty_delivered()
        self.assertEqual(line1.qty_delivered, 1.0)
        self.assertEqual(line2.qty_delivered, 2.0)

    def test_duplicate_bom_lines_same_product(self):
        """Test kit with duplicate BoM lines using the same product."""
        dup_kit = self.env["product.product"].create(
            {"name": "Dual Cable Kit", "type": "consu"}
        )
        cable = self.env["product.product"].create({"name": "Cable", "type": "consu"})
        dup_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": dup_kit.product_tmpl_id.id,
                "product_id": dup_kit.id,
                "type": "phantom",
                "product_qty": 1.0,
            }
        )
        line1 = self.env["mrp.bom.line"].create(
            {
                "bom_id": dup_bom.id,
                "product_id": cable.id,
                "product_qty": 2.0,
                "sequence": 1,
            }
        )
        line2 = self.env["mrp.bom.line"].create(
            {
                "bom_id": dup_bom.id,
                "product_id": cable.id,
                "product_qty": 3.0,
                "sequence": 2,
            }
        )

        order = self._create_sale_order()
        so_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": dup_kit.id,
                "product_uom_qty": 1.0,
                "price_unit": 50.0,
                "bom_id": dup_bom.id,
            }
        )
        self.assertEqual(len(so_line.kit_component_ids), 2)
        order.action_confirm()

        picking = order.picking_ids
        cable_moves = picking.move_ids.filtered(lambda m: m.product_id == cable)
        self.assertEqual(len(cable_moves), 2)
        move_line1 = cable_moves.filtered(lambda m: m.bom_line_id == line1)
        move_line2 = cable_moves.filtered(lambda m: m.bom_line_id == line2)
        self.assertEqual(move_line1.product_uom_qty, 2.0)
        self.assertEqual(move_line2.product_uom_qty, 3.0)

        for move in cable_moves:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.button_validate()

        so_line._compute_qty_delivered()
        self.assertEqual(so_line.qty_delivered, 1.0)

    def test_variant_specific_bom_components(self):
        """Test that only BoM components applicable to variant are populated."""
        color_attribute = self.env["product.attribute"].create(
            {
                "name": "Color",
                "create_variant": "always",
            }
        )
        color_red = self.env["product.attribute.value"].create(
            {
                "name": "Red",
                "attribute_id": color_attribute.id,
            }
        )
        color_blue = self.env["product.attribute.value"].create(
            {
                "name": "Blue",
                "attribute_id": color_attribute.id,
            }
        )
        var_tmpl = self.env["product.template"].create(
            {
                "name": "Customized Chassis",
                "type": "consu",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": color_attribute.id,
                            "value_ids": [Command.set([color_red.id, color_blue.id])],
                        }
                    )
                ],
            }
        )
        ptav_red = var_tmpl.attribute_line_ids.product_template_value_ids.filtered(
            lambda v: v.product_attribute_value_id == color_red
        )
        ptav_blue = var_tmpl.attribute_line_ids.product_template_value_ids.filtered(
            lambda v: v.product_attribute_value_id == color_blue
        )
        var_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": var_tmpl.id,
                "type": "phantom",
                "product_qty": 1.0,
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": var_bom.id,
                "product_id": self.comp_cpu.id,
                "product_qty": 1.0,
                "bom_product_template_attribute_value_ids": [
                    Command.set([ptav_red.id])
                ],
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": var_bom.id,
                "product_id": self.comp_ram.id,
                "product_qty": 1.0,
                "bom_product_template_attribute_value_ids": [
                    Command.set([ptav_blue.id])
                ],
            }
        )
        red_variant = var_tmpl.product_variant_ids.filtered(
            lambda p: ptav_red in p.product_template_attribute_value_ids
        )

        order = self._create_sale_order()
        var_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": red_variant.id,
                "product_uom_qty": 1.0,
                "price_unit": 200.0,
            }
        )
        # Should only populate CPU (applicable to Red), not RAM (applicable to Blue)
        self.assertEqual(len(var_line.kit_component_ids), 1)
        self.assertEqual(var_line.kit_component_ids.product_id, self.comp_cpu)

    def test_multi_step_warehouse_delivery(self):
        """Test that kit procurements do not re-explode on 2-step delivery routes."""
        self.warehouse.delivery_steps = "pick_ship"
        try:
            order = self._create_sale_order()
            line = self._create_kit_order_line(order, qty=1.0)
            order.action_confirm()

            self.assertEqual(order.state, "sale")
            self.assertTrue(order.picking_ids)
            # Delivery moves contain the components, not the parent kit
            delivery_products = order.picking_ids.move_ids.mapped("product_id")
            self.assertNotIn(self.kit_product, delivery_products)
            self.assertIn(self.comp_cpu, delivery_products)
            self.assertIn(self.comp_psu, delivery_products)

            # If multi-step pick moves exist, verify they also carry components
            orig_moves = line.move_ids.move_orig_ids
            if orig_moves:
                pick_products = orig_moves.mapped("product_id")
                self.assertNotIn(self.kit_product, pick_products)
                self.assertIn(self.comp_cpu, pick_products)
        finally:
            self.warehouse.delivery_steps = "ship_only"

    def test_sale_order_duplication(self):
        """Test that quotation duplication preserves customized kit components."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=1.0)
        ram_comp = line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_ram
        )
        ram_comp.is_selected = False
        psu_comp = line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_psu
        )
        psu_comp.product_qty = 3.0

        order_copy = order.copy()
        copy_line = order_copy.order_line[0]

        self.assertEqual(len(copy_line.kit_component_ids), 3)
        copy_ram = copy_line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_ram
        )
        self.assertFalse(copy_ram.is_selected)
        copy_psu = copy_line.kit_component_ids.filtered(
            lambda c: c.product_id == self.comp_psu
        )
        self.assertEqual(copy_psu.product_qty, 3.0)

    def test_cancellation_and_state_lock(self):
        """Test edit and reset restrictions on confirmed and cancelled orders."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=1.0)
        order.action_confirm()

        # Cannot reset on confirmed order
        with self.assertRaises(UserError):
            line.action_reload_kit_components()

        # Cannot modify component on confirmed order
        with self.assertRaises(UserError):
            line.kit_component_ids[0].write({"product_qty": 10.0})

        # Cannot delete component on confirmed order
        with self.assertRaises(UserError):
            line.kit_component_ids[0].unlink()

        # Cannot add new component on confirmed order
        with self.assertRaises(UserError):
            self.env["sale.order.line.kit.component"].create(
                {
                    "sale_line_id": line.id,
                    "product_id": self.comp_cpu.id,
                    "product_uom_id": self.comp_cpu.uom_id.id,
                }
            )

        # Cancel order
        order._action_cancel()
        with self.assertRaises(UserError):
            line.action_reload_kit_components()

        # Reset to draft
        order.action_draft()
        # Modifying component in draft is permitted
        line.kit_component_ids[0].product_qty = 4.0
        self.assertEqual(line.kit_component_ids[0].product_qty, 4.0)

    def test_negative_quantity_constraint(self):
        """Test that negative product quantities raise ValidationError."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=1.0)
        with self.assertRaises(ValidationError):
            line.kit_component_ids[0].product_qty = -2.0

    def test_action_open_kit_components(self):
        """Test the action opening the kit components form dialog."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=1.0)
        action = line.action_open_kit_components()
        self.assertEqual(action.get("type"), "ir.actions.act_window")
        self.assertEqual(action.get("res_id"), line.id)
        self.assertEqual(action.get("target"), "new")

    def test_write_product_id_sync(self):
        """Test that changing product_id on an order line updates kit components."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=1.0)
        self.assertTrue(line.kit_component_ids)

        # Change to non-kit product
        line.write({"product_id": self.std_product.id})
        self.assertFalse(line.is_kit)
        self.assertFalse(line.kit_component_ids)

        # Change back to kit product
        line.write({"product_id": self.kit_product.id})
        self.assertTrue(line.is_kit)
        self.assertEqual(len(line.kit_component_ids), 3)

    def test_create_fallback_from_bom_line(self):
        """Test fallback population of product_id and UoM when bom_line_id is given."""
        order = self._create_sale_order()
        line = self._create_kit_order_line(order, qty=1.0)
        comp = self.env["sale.order.line.kit.component"].create(
            {
                "sale_line_id": line.id,
                "bom_line_id": self.bom_line_cpu.id,
                "product_qty": 2.0,
            }
        )
        self.assertEqual(comp.product_id, self.comp_cpu)
        self.assertEqual(comp.product_uom_id, self.comp_cpu.uom_id)

    def test_multi_record_write_product_id_bom_isolation(self):
        """Test multi-record write() updates bom_id independently per record."""
        other_kit_tmpl = self.env["product.template"].create(
            {"name": "Other Kit Template", "type": "consu"}
        )
        other_kit_product = other_kit_tmpl.product_variant_id
        other_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": other_kit_tmpl.id,
                "product_id": other_kit_product.id,
                "type": "phantom",
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create({"product_id": self.comp_cpu.id, "product_qty": 2.0})
                ],
            }
        )

        order = self._create_sale_order()
        line1 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.kit_product.id,
                "product_uom_qty": 1.0,
                "bom_id": self.kit_bom.id,
            }
        )
        line2 = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": other_kit_product.id,
                "product_uom_qty": 1.0,
                "bom_id": other_bom.id,
            }
        )
        self.assertEqual(line1.bom_id, self.kit_bom)
        self.assertEqual(line2.bom_id, other_bom)

        # Batch write: change product_id on both lines to self.kit_product
        # line1 already matches self.kit_bom, so its bom_id must be preserved
        # line2 switches from other_kit_product, so other_bom must be cleared
        (line1 | line2).write({"product_id": self.kit_product.id})

        self.assertEqual(line1.product_id, self.kit_product)
        self.assertEqual(line1.bom_id, self.kit_bom)
        self.assertEqual(line2.product_id, self.kit_product)
        self.assertFalse(line2.bom_id)
        self.assertTrue(line1.is_kit)
        self.assertTrue(line2.is_kit)
        self.assertEqual(len(line1.kit_component_ids), 3)
        self.assertEqual(len(line2.kit_component_ids), 3)

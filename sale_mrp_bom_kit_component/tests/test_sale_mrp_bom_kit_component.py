# Copyright 2026 Eshan Desle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
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

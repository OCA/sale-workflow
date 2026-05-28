# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestSaleProcurementGroupByLine(TransactionCase):
    def setUp(self):
        super(TestSaleProcurementGroupByLine, self).setUp()
        # Required Models
        self.product_model = self.env["product.product"]
        self.product_ctg_model = self.env["product.category"]
        self.proc_group_model = self.env["procurement.group"]
        self.sale_model = self.env["sale.order"]
        self.order_line_model = self.env["sale.order.line"]
        # Customer
        self.customer = self.env.ref("base.res_partner_2")
        # Warehouse
        self.warehouse_id = self.env.ref("stock.warehouse0")
        # Create product category
        self.product_ctg = self._create_product_category()
        # Create Products
        self.new_product1 = self._create_product("test_product1")
        self.new_product2 = self._create_product("test_product2")
        self.sale = self._create_sale_order()

    def _create_product_category(self):
        product_ctg = self.product_ctg_model.create({"name": "test_product_ctg"})
        return product_ctg

    def _create_product(self, name):
        product = self.product_model.create(
            {"name": name, "categ_id": self.product_ctg.id, "type": "product"}
        )
        return product

    def _create_sale_order(self):
        """Create a Sale Order."""
        self.sale = self.sale_model.create(
            {
                "partner_id": self.customer.id,
                "warehouse_id": self.warehouse_id.id,
                "picking_policy": "direct",
            }
        )
        self.line1 = self.order_line_model.create(
            {
                "order_id": self.sale.id,
                "product_id": self.new_product1.id,
                "product_uom_qty": 10.0,
                "name": "Sale Order Line Demo1",
            }
        )
        self.line2 = self.order_line_model.create(
            {
                "order_id": self.sale.id,
                "product_id": self.new_product2.id,
                "product_uom_qty": 5.0,
                "name": "Sale Order Line Demo2",
            }
        )
        return self.sale

    def _create_kit_product(self, name, components):
        """Create a storable product with a phantom (kit) BoM."""
        kit_product = self.product_model.create(
            {
                "name": name,
                "categ_id": self.product_ctg.id,
                "type": "product",
            }
        )
        self.env["mrp.bom"].create(
            {
                "product_id": kit_product.id,
                "product_tmpl_id": kit_product.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [
                    (0, 0, {"product_id": comp.id, "product_qty": 1.0})
                    for comp in components
                ],
            }
        )
        return kit_product

    def test_01_procurement_group_by_line(self):
        self.sale.action_confirm()
        self.assertEqual(
            self.line2.procurement_group_id,
            self.line1.procurement_group_id,
            """Both Sale Order line should belong
                         to Procurement Group""",
        )
        self.picking_ids = self.env["stock.picking"].search(
            [("group_id", "in", self.line2.procurement_group_id.ids)]
        )
        self.picking_ids.move_lines.write({"quantity_done": 5})
        wiz_act = self.picking_ids.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(wiz_act["context"])
        ).save()
        wiz.process()
        self.assertTrue(self.picking_ids, "Procurement Group should have picking")

    def test_02_action_launch_procurement_rule_1(self):
        group_id = self.proc_group_model.create(
            {"move_type": "one", "sale_id": self.sale.id, "name": self.sale.name}
        )
        self.line1.procurement_group_id = group_id
        self.line2.procurement_group_id = group_id
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "sale")
        self.assertEqual(len(self.line1.move_ids), 1)
        self.assertEqual(self.line1.move_ids.name, self.line1.product_id.display_name)
        self.assertEqual(len(self.line2.move_ids), 1)
        self.assertEqual(self.line2.move_ids.name, self.line2.product_id.display_name)

    def test_03_action_launch_procurement_rule_2(self):
        group_id = self.proc_group_model.create(
            {"move_type": "one", "sale_id": self.sale.id, "name": self.sale.name}
        )
        self.line1.procurement_group_id = group_id
        self.line2.procurement_group_id = False
        self.sale.action_confirm()
        self.assertEqual(self.line2.procurement_group_id, group_id)

    def test_04_action_launch_procurement_rule_3(self):
        group_id = self.proc_group_model.create(
            {"move_type": "one", "sale_id": self.sale.id, "name": self.sale.name}
        )
        self.line1.procurement_group_id = False
        self.line2.procurement_group_id = False
        self.sale.action_confirm()
        self.assertNotEqual(self.line1.procurement_group_id, group_id)
        self.assertEqual(
            self.line1.procurement_group_id, self.line2.procurement_group_id
        )

    def test_05_merged_stock_moves_from_same_procurement(self):
        """
        Reduce the qty in the sale order and check no extra picking is created
        """
        self.sale.action_confirm()
        self.sale.order_line[1].product_uom_qty = 0.0
        self.assertEqual(
            len(self.sale.picking_ids), 1, "Negative stock move should me merged"
        )

    def test_06_update_sale_order_line_respect_procurement_group(self):
        """
        When launching the stock rule again, use maintain same procurement group in lines
        """
        self.sale.action_confirm()
        proc_group = self.sale.order_line[1].procurement_group_id
        self.assertEqual(len(self.line1.move_ids), 1)
        self.sale.order_line[1].product_uom_qty += 1
        self.assertEqual(self.sale.order_line[1].procurement_group_id, proc_group)
        self.assertEqual(len(self.line1.move_ids), 1)

    def test_07_nested_kit_no_double_procurement(self):
        """Selling a kit whose BoM contains a component that is itself a kit
        should create exactly one stock move per leaf component, not doubled.
        """
        leaf1 = self.product_model.create(
            {
                "name": "leaf_component_1",
                "categ_id": self.product_ctg.id,
                "type": "product",
            }
        )
        leaf2 = self.product_model.create(
            {
                "name": "leaf_component_2",
                "categ_id": self.product_ctg.id,
                "type": "product",
            }
        )
        inner_kit = self._create_kit_product("inner_kit", [leaf1, leaf2])
        plain = self.product_model.create(
            {
                "name": "plain_component",
                "categ_id": self.product_ctg.id,
                "type": "product",
            }
        )
        outer_kit = self._create_kit_product("outer_kit", [plain, inner_kit])
        sale = self.sale_model.create(
            {
                "partner_id": self.customer.id,
                "warehouse_id": self.warehouse_id.id,
                "picking_policy": "direct",
            }
        )
        self.order_line_model.create(
            {
                "order_id": sale.id,
                "product_id": outer_kit.id,
                "product_uom_qty": 1.0,
                "name": "Nested kit sale line",
            }
        )
        # Simulate the sale_mrp _get_qty_procurement bug: for any product with
        # a phantom BoM, return 0 — as if component moves don't match.
        # This is what causes super() to re-run procurement on nested kits.
        original = self.env["sale.order.line"].__class__._get_qty_procurement

        def broken_get_qty_procurement(self_line, previous_product_uom_qty=False):
            bom = self_line.env["mrp.bom"]._bom_find(
                product=self_line.product_id, bom_type="phantom"
            )
            if bom:
                return 0.0
            return original(self_line, previous_product_uom_qty)

        self.env[
            "sale.order.line"
        ].__class__._get_qty_procurement = broken_get_qty_procurement
        try:
            sale.action_confirm()
        finally:
            self.env["sale.order.line"].__class__._get_qty_procurement = original
        all_moves = sale.picking_ids.mapped("move_lines")
        self.assertEqual(len(all_moves), 3)
        for move in all_moves:
            # without fix quantity is 2
            self.assertEqual(move.product_uom_qty, 1.0)

# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.sale_stock.tests.common import TestSaleStockCommon


class TestSaleStockReferenceByLine(TestSaleStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Required Models
        cls.product_model = cls.env["product.product"]
        cls.product_ctg_model = cls.env["product.category"]
        cls.proc_group_model = cls.env["stock.reference"]
        cls.sale_model = cls.env["sale.order"]
        cls.order_line_model = cls.env["sale.order.line"]
        # Warehouse
        cls.warehouse_id = cls.env.ref("stock.warehouse0")
        # Create product category
        cls.product_ctg = cls._create_product_category()
        # Create Products
        cls.new_product1 = cls._create_product(
            name="test_product1",
            categ_id=cls.product_ctg.id,
            is_storable=True,
        )
        cls.new_product2 = cls._create_product(
            name="test_product2",
            categ_id=cls.product_ctg.id,
            is_storable=True,
        )
        cls.sale = cls._create_sale_order()

    @classmethod
    def _create_product_category(cls):
        product_ctg = cls.product_ctg_model.create({"name": "test_product_ctg"})
        return product_ctg

    @classmethod
    def _create_sale_order(cls):
        """Create a Sale Order."""
        cls.sale = cls.sale_model.create(
            {
                "partner_id": cls.partner_a.id,
                "warehouse_id": cls.warehouse_id.id,
                "picking_policy": "direct",
            }
        )
        cls.line1 = cls.order_line_model.create(
            {
                "order_id": cls.sale.id,
                "product_id": cls.new_product1.id,
                "product_uom_qty": 10.0,
                "name": "Sale Order Line Demo1",
            }
        )
        cls.line2 = cls.order_line_model.create(
            {
                "order_id": cls.sale.id,
                "product_id": cls.new_product2.id,
                "product_uom_qty": 5.0,
                "name": "Sale Order Line Demo2",
            }
        )
        return cls.sale

    def test_01_stock_reference_by_line(self):
        self.sale.action_confirm()
        self.assertEqual(
            self.line2.stock_reference_id,
            self.line1.stock_reference_id,
            """Both Sale Order line should belong
                         to Stock Reference""",
        )
        self.picking_ids = self.env["stock.picking"].search(
            [("reference_ids", "in", self.line2.stock_reference_id.ids)]
        )
        self.picking_ids.move_ids.write({"quantity": 5})
        wiz_act = self.picking_ids.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(**wiz_act["context"])
        ).save()
        wiz.process()
        self.assertTrue(self.picking_ids, "Stock reference should have picking")

    def test_02_action_launch_procurement_rule_1(self):
        stock_ref = self.proc_group_model.create(
            {
                "sale_ids": [(6, 0, self.sale.ids)],
                "name": self.sale.name,
            },
        )
        self.line1.stock_reference_id = stock_ref
        self.line2.stock_reference_id = stock_ref
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "sale")
        self.assertEqual(len(self.line1.move_ids), 1)
        self.assertEqual(len(self.line2.move_ids), 1)

    def test_03_action_launch_procurement_rule_2(self):
        stock_ref = self.proc_group_model.create(
            {
                "sale_ids": [(6, 0, self.sale.ids)],
                "name": self.sale.name,
            },
        )
        self.line1.stock_reference_id = stock_ref
        self.line2.stock_reference_id = False
        self.sale.action_confirm()
        self.assertEqual(self.line2.stock_reference_id, stock_ref)

    def test_04_action_launch_procurement_rule_3(self):
        stock_ref = self.proc_group_model.create(
            {
                "sale_ids": [(6, 0, self.sale.ids)],
                "name": self.sale.name,
            },
        )
        self.line1.stock_reference_id = False
        self.line2.stock_reference_id = False
        self.sale.action_confirm()
        self.assertNotEqual(self.line1.stock_reference_id, stock_ref)
        self.assertEqual(self.line1.stock_reference_id, self.line2.stock_reference_id)

    def test_05_merged_stock_moves_from_same_procurement(self):
        """
        Reduce the qty in the sale order and check no extra picking is created
        """
        self.sale.action_confirm()
        self.sale.order_line[1].product_uom_qty = 0.0
        self.assertEqual(
            len(self.sale.picking_ids), 1, "Negative stock move should me merged"
        )

    def test_06_update_sale_order_line_respect_stock_reference(self):
        """
        When launching the stock rule again,
        use maintain same stock reference in lines
        """
        self.sale.action_confirm()
        stock_ref = self.sale.order_line[1].stock_reference_id
        self.assertEqual(len(self.line1.move_ids), 1)
        self.sale.order_line[1].product_uom_qty += 1
        self.assertEqual(self.sale.order_line[1].stock_reference_id, stock_ref)
        self.assertEqual(len(self.line1.move_ids), 1)

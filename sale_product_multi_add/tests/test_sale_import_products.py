# Copyright 2025 Max He
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestSaleImportProducts(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "list_price": 100.0,
                "type": "consu",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "list_price": 50.0,
                "type": "consu",
            }
        )

    def _create_wizard_with_items(self, products):
        wizard = self.env["sale.import.products"].create(
            {"products": [(6, 0, [p.id for p in products])]}
        )
        wizard.create_items()
        return wizard

    def test_create_items(self):
        """Test the create_items method of the wizard"""
        wizard = self._create_wizard_with_items(self.product_1 | self.product_2)
        self.assertEqual(len(wizard.items), 2)

    def test_create_items_returns_action(self):
        """Test that create_items returns an action opening the wizard"""
        wizard = self._create_wizard_with_items(self.product_1 | self.product_2)
        result = wizard.create_items()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "sale.import.products")

    def test_create_items_empty_products(self):
        """Test create_items method with empty products list"""
        wizard = self.env["sale.import.products"].create({"products": [(6, 0, [])]})
        result = wizard.create_items()
        self.assertEqual(len(wizard.items), 0)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "sale.import.products")

    def test_get_line_values(self):
        """Test the _get_line_values method"""
        partner = self.env.ref("base.res_partner_2")
        so = self.env["sale.order"].create({"partner_id": partner.id})
        wizard = self._create_wizard_with_items(self.product_1)
        item = wizard.items[0]
        item.quantity = 5.0

        line_values = wizard._get_line_values(so, item)

        self.assertIsInstance(line_values, dict)
        self.assertEqual(line_values["product_id"], self.product_1.id)
        self.assertEqual(line_values["product_uom_qty"], 5.0)
        self.assertEqual(line_values["product_uom"], self.product_1.uom_id.id)

    def test_select_products_with_pricelist(self):
        """The order pricelist price is applied to the created sale order line"""
        partner = self.env.ref("base.res_partner_2")
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Test Pricelist with 10% Discount",
                "currency_id": self.env.company.currency_id.id,
            }
        )
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": pricelist.id,
                "applied_on": "3_global",
                "compute_price": "percentage",
                "percent_price": 10.0,
            }
        )
        so = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "pricelist_id": pricelist.id,
            }
        )
        wizard = self._create_wizard_with_items(self.product_1)
        wizard.items[0].quantity = 2.0

        wizard.with_context(
            active_id=so.id, active_model="sale.order"
        ).select_products()

        self.assertEqual(len(so.order_line), 1)
        self.assertEqual(so.order_line.product_uom_qty, 2.0)
        # Pricelist grants 10% off the 100.0 list price
        self.assertNotEqual(so.order_line.price_unit, self.product_1.list_price)
        self.assertAlmostEqual(so.order_line.price_unit, 90.0, places=2)

    def test_select_products_without_pricelist(self):
        """Without pricelist rules the product list price is used"""
        partner = self.env.ref("base.res_partner_2")
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Empty Pricelist",
                "currency_id": self.env.company.currency_id.id,
            }
        )
        so = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "pricelist_id": pricelist.id,
            }
        )
        wizard = self._create_wizard_with_items(self.product_2)
        wizard.items[0].quantity = 3.0

        wizard.with_context(
            active_id=so.id, active_model="sale.order"
        ).select_products()

        self.assertEqual(len(so.order_line), 1)
        self.assertEqual(so.order_line.product_uom_qty, 3.0)
        self.assertAlmostEqual(
            so.order_line.price_unit, self.product_2.list_price, places=2
        )

    def test_select_products(self):
        """Test the select_products method of the wizard"""
        partner = self.env.ref("base.res_partner_2")
        so = self.env["sale.order"].create({"partner_id": partner.id})
        wizard = self._create_wizard_with_items(self.product_1 | self.product_2)
        for item in wizard.items:
            if item.product_id == self.product_1:
                item.quantity = 2.0
            else:
                item.quantity = 3.0

        result = wizard.with_context(
            active_id=so.id, active_model="sale.order"
        ).select_products()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window_close")
        self.assertEqual(len(so.order_line), 2)
        line1 = so.order_line.filtered(lambda line: line.product_id == self.product_1)
        line2 = so.order_line.filtered(lambda line: line.product_id == self.product_2)
        self.assertEqual(line1.product_uom_qty, 2.0)
        self.assertEqual(line2.product_uom_qty, 3.0)

    def test_select_products_no_sale_order(self):
        """Test select_products method when no sale order is found"""
        wizard = self._create_wizard_with_items(self.product_1)
        wizard.items[0].quantity = 1.0

        result = wizard.select_products()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window_close")

    def test_select_products_empty_items(self):
        """Test select_products method with empty items list"""
        partner = self.env.ref("base.res_partner_2")
        so = self.env["sale.order"].create({"partner_id": partner.id})
        wizard = self.env["sale.import.products"].create({"products": [(6, 0, [])]})

        result = wizard.with_context(
            active_id=so.id, active_model="sale.order"
        ).select_products()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window_close")
        self.assertEqual(len(so.order_line), 0)

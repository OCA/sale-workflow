from unittest.mock import patch

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSale(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_9 = cls.env["product.product"].create(
            {"name": "Test Product 9", "type": "consu"}
        )
        cls.product_11 = cls.env["product.product"].create(
            {"name": "Test Product 11", "type": "consu"}
        )
        cls.product_priced = cls.env["product.product"].create(
            {"name": "Test Product Priced", "type": "consu", "list_price": 100.0}
        )
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "picking_policy": "one",
            }
        )

    def test_import_product(self):
        """Create SO
        Import products
        Check products are present
        """
        wiz_obj = self.env["sale.import.products"]
        wizard = wiz_obj.with_context(active_id=self.so.id, active_model="sale.order")

        products = [Command.set([self.product_9.id, self.product_11.id])]

        wizard_id = wizard.create([{"products": products}])
        wizard_id.create_items()
        wizard_id.items[0].quantity = 4
        wizard_id.items[1].quantity = 6
        wizard_id.select_products()

        self.assertEqual(len(self.so.order_line), 2)

        for line in self.so.order_line:
            if line.product_id.id == self.product_9.id:
                self.assertEqual(line.product_uom_qty, 4)
            else:
                self.assertEqual(line.product_uom_qty, 6)

    def test_select_products_no_vals(self):
        """Test when _get_line_values returns False"""
        wizard = self.env["sale.import.products"].create([])

        # Use unittest.mock to patch the method instead of direct assignment
        with patch.object(type(wizard), "_get_line_values", return_value=False):
            wizard.with_context(active_id=self.so.id).select_products()

        # Assert that no order lines are created
        self.assertEqual(len(self.so.order_line), 0)

    def test_select_products_empty_vals_list(self):
        """Test when vals_list is empty"""
        wizard = self.env["sale.import.products"].create([])
        wizard.with_context(active_id=self.so.id).select_products()

        # Assert that no order lines are created
        self.assertEqual(len(self.so.order_line), 0)

    def test_select_products_no_sale(self):
        """Test when sale is not found"""
        wizard = self.env["sale.import.products"].create([])
        result = wizard.with_context(active_id=False).select_products()

        # Assert no order lines are created and window action is returned
        self.assertEqual(len(self.so.order_line), 0)
        self.assertEqual(result, {"type": "ir.actions.act_window_close"})

    def test_select_products_with_vals(self):
        """Test when vals_list is created"""
        wiz_obj = self.env["sale.import.products"]
        wizard = wiz_obj.with_context(active_id=self.so.id)
        products = [Command.set([self.product_9.id, self.product_11.id])]
        wizard_id = wizard.create([{"products": products}])
        wizard_id.create_items()
        wizard_id.items[0].quantity = 3
        wizard_id.items[1].quantity = 5
        wizard_id.select_products()

        # Assert that order lines are created correctly
        self.assertEqual(len(self.so.order_line), 2)
        for line in self.so.order_line:
            if line.product_id.id == self.product_9.id:
                self.assertEqual(line.product_uom_qty, 3)
            elif line.product_id.id == self.product_11.id:
                self.assertEqual(line.product_uom_qty, 5)

    def _import_product(self, sale, product, quantity):
        wizard = self.env["sale.import.products"].with_context(
            active_id=sale.id, active_model="sale.order"
        )
        wizard_id = wizard.create([{"products": [Command.set([product.id])]}])
        wizard_id.create_items()
        wizard_id.items[0].quantity = quantity
        wizard_id.select_products()
        return sale.order_line.filtered(lambda line: line.product_id == product)

    def test_select_products_applies_pricelist(self):
        """The order pricelist price is applied to the created sale order line"""
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
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
            }
        )

        line = self._import_product(sale, self.product_priced, 2.0)

        self.assertEqual(len(sale.order_line), 1)
        self.assertEqual(line.product_uom_qty, 2.0)
        # Pricelist grants 10% off the 100.0 list price
        self.assertNotEqual(line.price_unit, self.product_priced.list_price)
        self.assertAlmostEqual(line.price_unit, 90.0, places=2)

    def test_select_products_without_pricelist_rule(self):
        """Without pricelist rules the product list price is used"""
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Empty Pricelist",
                "currency_id": self.env.company.currency_id.id,
            }
        )
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
            }
        )

        line = self._import_product(sale, self.product_priced, 3.0)

        self.assertEqual(len(sale.order_line), 1)
        self.assertEqual(line.product_uom_qty, 3.0)
        self.assertAlmostEqual(
            line.price_unit, self.product_priced.list_price, places=2
        )

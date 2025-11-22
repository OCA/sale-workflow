# Copyright 2024 Your Name
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import UserError


class TestCoverageImprovement(common.TransactionCase):
    def setUp(self):
        super().setUp()
        # Create test products
        self.product_1 = self.env["product.product"].create(
            {
                "name": "Test Product 1",
                "list_price": 100.0,
                "type": "consu",
            }
        )
        self.product_2 = self.env["product.product"].create(
            {
                "name": "Test Product 2",
                "list_price": 50.0,
                "type": "consu",
            }
        )

    def test_get_line_values_with_pricelist(self):
        """Test _get_line_values method with pricelist pricing"""
        # Create a partner and pricelist
        partner = self.env.ref("base.res_partner_2")
        pricelist = self.env["product.pricelist"].create({
            "name": "Test Pricelist",
            "currency_id": self.env.ref("base.EUR").id,
        })
        
        # Create a sale order with pricelist
        so = self.env["sale.order"].create({
            "partner_id": partner.id,
            "pricelist_id": pricelist.id,
        })

        # Create wizard
        wizard = self.env["sale.import.products"].create(
            {"products": [(6, 0, [self.product_1.id])]}
        )

        # Create items
        wizard.create_items()

        # Set quantity
        item = wizard.items[0]
        item.quantity = 2.0

        # Test _get_line_values method
        line_values = wizard._get_line_values(so, item)

        # Check that the returned values are correct
        self.assertIsInstance(line_values, dict)
        self.assertEqual(line_values["product_id"], self.product_1.id)
        self.assertEqual(line_values["product_uom_qty"], 2.0)
        self.assertEqual(line_values["product_uom"], self.product_1.uom_id.id)

    def test_get_line_values_without_pricelist(self):
        """Test _get_line_values method without pricelist (fallback to list_price)"""
        # Create a sale order without pricelist
        partner = self.env.ref("base.res_partner_2")
        so = self.env["sale.order"].create({"partner_id": partner.id})

        # Create wizard
        wizard = self.env["sale.import.products"].create(
            {"products": [(6, 0, [self.product_2.id])]}
        )

        # Create items
        wizard.create_items()

        # Set quantity
        item = wizard.items[0]
        item.quantity = 3.0

        # Test _get_line_values method
        line_values = wizard._get_line_values(so, item)

        # Check that the returned values are correct
        self.assertIsInstance(line_values, dict)
        self.assertEqual(line_values["product_id"], self.product_2.id)
        self.assertEqual(line_values["product_uom_qty"], 3.0)
        self.assertEqual(line_values["product_uom"], self.product_2.uom_id.id)

    def test_create_items_empty_products(self):
        """Test create_items method with empty products list"""
        # Create wizard with no products
        wizard = self.env["sale.import.products"].create({"products": [(6, 0, [])]})

        # Test create_items method
        result = wizard.create_items()

        # Check that no items were created
        self.assertEqual(len(wizard.items), 0)

        # Check that the action returned is correct
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "sale.import.products")

    def test_select_products_no_sale_order(self):
        """Test select_products method when no sale order is found"""
        # Create wizard
        wizard = self.env["sale.import.products"].create(
            {"products": [(6, 0, [self.product_1.id])]}
        )

        # Create items
        wizard.create_items()

        # Set quantity
        wizard.items[0].quantity = 1.0

        # Test select_products method without proper context
        result = wizard.select_products()

        # Check that the action returned is correct
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window_close")

    def test_select_products_empty_items(self):
        """Test select_products method with empty items list"""
        # Create a sale order
        partner = self.env.ref("base.res_partner_2")
        so = self.env["sale.order"].create({"partner_id": partner.id})

        # Create wizard with no products
        wizard = self.env["sale.import.products"].create({"products": [(6, 0, [])]})

        # Test select_products method with proper context
        wizard_ctx = wizard.with_context(active_id=so.id, active_model="sale.order")
        result = wizard_ctx.select_products()

        # Check that the action returned is correct
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window_close")
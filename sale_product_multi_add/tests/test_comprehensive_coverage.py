# Copyright 2024 Your Name
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestComprehensiveCoverage(common.TransactionCase):
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

    def test_create_items_method(self):
        """Test create_items method"""
        # Create a sale order
        partner = self.env.ref("base.res_partner_2")
        so = self.env["sale.order"].create({
            "partner_id": partner.id,
        })
        
        # Create wizard with context
        wizard = self.env["sale.import.products"].with_context(
            active_id=so.id, 
            active_model="sale.order"
        ).create({
            "products": [(6, 0, [self.product_1.id, self.product_2.id])]
        })
        
        # Test create_items method
        result = wizard.create_items()
        
        # Check that two items were created
        self.assertEqual(len(wizard.items), 2)
        
        # Check that the action returned is correct
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "sale.import.products")

    def test_select_products_method(self):
        """Test select_products method"""
        # Create a sale order
        partner = self.env.ref("base.res_partner_2")
        so = self.env["sale.order"].create({
            "partner_id": partner.id,
        })
        
        # Create wizard with context
        wizard = self.env["sale.import.products"].with_context(
            active_id=so.id, 
            active_model="sale.order"
        ).create({
            "products": [(6, 0, [self.product_1.id])]
        })
        
        # Create items
        wizard.create_items()
        
        # Set quantity
        wizard.items[0].quantity = 3.0
        
        # Test select_products method
        result = wizard.select_products()
        
        # Check that one order line was created
        self.assertEqual(len(so.order_line), 1)
        self.assertEqual(so.order_line[0].product_uom_qty, 3.0)
        self.assertEqual(so.order_line[0].product_id, self.product_1)
        
        # Check that the action returned is correct
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window_close")

    def test_get_line_values_method(self):
        """Test _get_line_values method"""
        # Create a sale order
        partner = self.env.ref("base.res_partner_2")
        so = self.env["sale.order"].create({
            "partner_id": partner.id,
        })
        
        # Create wizard with context
        wizard = self.env["sale.import.products"].with_context(
            active_id=so.id, 
            active_model="sale.order"
        ).create({
            "products": [(6, 0, [self.product_1.id])]
        })
        
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
        self.assertEqual(line_values["price_unit"], self.product_1.list_price)

    def test_get_line_values_method_with_pricelist(self):
        """Test _get_line_values method with pricelist"""
        # Create a pricelist
        pricelist = self.env["product.pricelist"].create({
            "name": "Test Pricelist",
            "currency_id": self.env.ref("base.EUR").id,
        })
        
        # Create a sale order with pricelist
        partner = self.env.ref("base.res_partner_2")
        so = self.env["sale.order"].create({
            "partner_id": partner.id,
            "pricelist_id": pricelist.id,
        })

        # Create wizard with context
        wizard = self.env["sale.import.products"].with_context(
            active_id=so.id, 
            active_model="sale.order"
        ).create({
            "products": [(6, 0, [self.product_1.id])]
        })

        # Create items
        wizard.create_items()

        # Set quantity
        item = wizard.items[0]
        item.quantity = 3.0

        # Test _get_line_values method with pricelist
        line_values = wizard._get_line_values(so, item)

        # Check that the returned values are correct
        self.assertIsInstance(line_values, dict)
        self.assertEqual(line_values["product_id"], self.product_1.id)
        self.assertEqual(line_values["product_uom_qty"], 3.0)
        self.assertEqual(line_values["product_uom"], self.product_1.uom_id.id)

    def test_sale_import_products_item_model(self):
        """Test SaleImportProductsItem model"""
        # Create a wizard first
        wizard = self.env["sale.import.products"].create({
            "products": [(6, 0, [self.product_1.id])]
        })
        
        # Create an item
        item = self.env["sale.import.products.items"].create({
            "wizard_id": wizard.id,
            "product_id": self.product_1.id,
            "quantity": 5.0,
        })
        
        # Check that the item was created correctly
        self.assertEqual(item.wizard_id, wizard)
        self.assertEqual(item.product_id, self.product_1)
        self.assertEqual(item.quantity, 5.0)

    def test_select_products_without_sale_order(self):
        """Test select_products method without active sale order"""
        # Create wizard without context
        wizard = self.env["sale.import.products"].create({
            "products": [(6, 0, [self.product_1.id])]
        })
        
        # Create items
        wizard.create_items()
        
        # Set quantity
        wizard.items[0].quantity = 2.0
        
        # Test select_products method without active sale order
        result = wizard.select_products()
        
        # Check that the action returned is correct
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window_close")
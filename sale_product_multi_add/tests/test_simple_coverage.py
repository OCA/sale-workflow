# Copyright 2024 Your Name
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestSimpleCoverage(common.TransactionCase):
    def test_basic_functionality(self):
        """Test basic functionality of the module"""
        # Create test products
        product_1 = self.env["product.product"].create(
            {
                "name": "Test Product 1",
                "list_price": 100.0,
                "type": "consu",
            }
        )
        
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
            "products": [(6, 0, [product_1.id])]
        })
        
        # Test create_items method
        result = wizard.create_items()
        
        # Check that one item was created
        self.assertEqual(len(wizard.items), 1)
        
        # Set quantity
        wizard.items[0].quantity = 3.0
        
        # Test select_products method
        result = wizard.select_products()
        
        # Check that one order line was created
        self.assertEqual(len(so.order_line), 1)
        self.assertEqual(so.order_line[0].product_uom_qty, 3.0)
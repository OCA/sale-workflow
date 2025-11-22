# Copyright 2024 Your Name
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestEnhancedCoverage(common.TransactionCase):

    def setUp(self):
        super().setUp()
        # Create test products
        self.product_1 = self.env['product.product'].create({
            'name': 'Test Product 1',
            'list_price': 100.0,
            'type': 'consu',
        })
        self.product_2 = self.env['product.product'].create({
            'name': 'Test Product 2',
            'list_price': 50.0,
            'type': 'consu',
        })

    def test_create_items_method(self):
        """Test the create_items method of the wizard"""
        wizard = self.env['sale.import.products'].create({
            'products': [(6, 0, [self.product_1.id, self.product_2.id])]
        })
        
        # Test create_items method
        result = wizard.create_items()
        
        # Check that items were created
        self.assertEqual(len(wizard.items), 2)
        
        # Check that the action returned is correct
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'sale.import.products')

    def test_select_products_method(self):
        """Test the select_products method of the wizard"""
        # Create a sale order
        partner = self.env.ref('base.res_partner_2')
        so = self.env['sale.order'].create({'partner_id': partner.id})
        
        # Create wizard
        wizard = self.env['sale.import.products'].create({
            'products': [(6, 0, [self.product_1.id, self.product_2.id])]
        })
        
        # Create items
        wizard.create_items()
        
        # Set quantities
        for item in wizard.items:
            if item.product_id.id == self.product_1.id:
                item.quantity = 2.0
            elif item.product_id.id == self.product_2.id:
                item.quantity = 3.0
        
        # Test select_products method with proper context
        wizard_ctx = wizard.with_context(active_id=so.id, active_model='sale.order')
        result = wizard_ctx.select_products()
        
        # Check that the action returned is correct
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'ir.actions.act_window_close')
        
        # Check that sale order lines were created
        self.assertEqual(len(so.order_line), 2)

    def test_get_line_values_method(self):
        """Test the _get_line_values method"""
        # Create a sale order
        partner = self.env.ref('base.res_partner_2')
        so = self.env['sale.order'].create({'partner_id': partner.id})
        
        # Create wizard
        wizard = self.env['sale.import.products'].create({
            'products': [(6, 0, [self.product_1.id])]
        })
        
        # Create items
        wizard.create_items()
        
        # Set quantity
        item = wizard.items[0]
        item.quantity = 5.0
        
        # Test _get_line_values method
        line_values = wizard._get_line_values(so, item)
        
        # Check that the returned values are correct
        self.assertIsInstance(line_values, dict)
        self.assertEqual(line_values['product_id'], self.product_1.id)
        self.assertEqual(line_values['product_uom_qty'], 5.0)
        self.assertEqual(line_values['product_uom'], self.product_1.uom_id.id)
# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestDisableInventoryCheck(common.TransactionCase):

    def setUp(self):
        super(TestDisableInventoryCheck, self).setUp()

        self.category_1 = self.env['product.category'].create({
            'name': 'Category 1',
            'check_stock_on_sale': True,
        })
        self.category_2 = self.env['product.category'].create({
            'name': 'Category 2',
            'check_stock_on_sale': True,
        })

        # Create stockable product
        self.product_1 = self.env['product.product'].create({
            'name': 'Product 1',
            'type': 'product',
            'uom_id': self.ref('product.product_uom_unit'),
            'check_stock_on_sale': 'skip',
            'categ_id': self.category_1.id,
        })
        self.product_2 = self.env['product.product'].create({
            'name': 'Product 2',
            'type': 'product',
            'uom_id': self.ref('product.product_uom_unit'),
            'check_stock_on_sale': 'defer',
            'categ_id': self.category_2.id,
        })

    def test_disable_inventory_check(self):
        # Create an empty sale order
        order = self.env['sale.order'].new({
            'partner_id': 1,
            'warehouse_id': 1,
            'state': 'draft',
        })
        # Sale product_1 with quantity is 15
        order_line1 = self.env['sale.order.line'].new({
            'order_id': order.id,
            'product_id': self.product_1.id,
            'product_uom': self.product_1.uom_id.id,
            'product_uom_qty': 15,
        })
        res1 = order_line1._onchange_product_id_check_availability()
        self.assertNotIn('warning', res1, "There should not be a warning!!!")
        # Sale product_2 with quantity is 15
        order_line2 = self.env['sale.order.line'].new({
            'order_id': order.id,
            'product_id': self.product_2.id,
            'product_uom': self.product_2.uom_id.id,
            'product_uom_qty': 15,
        })
        res2 = order_line2._onchange_product_id_check_availability()
        self.assertIn('warning', res2, "Should have returned a warning")
        self.assertIsInstance(
            res2['warning'], dict, "Warning should be a dictionary")
        self.assertIn('title', res2['warning'], "Warning should have a title")
        self.assertEqual(
            res2['warning']['title'], 'Not enough inventory!',
            "There should be a warning!!!")

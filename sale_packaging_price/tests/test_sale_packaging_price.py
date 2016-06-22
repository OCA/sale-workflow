# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl
from openerp.tests.common import TransactionCase


class TestSalePackagingPrice(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestSalePackagingPrice, self).setUp()
        self.product = self.env.ref('product.product_product_6')
        self.product.product_tmpl_id.lst_price = 10.0
        self.product.product_tmpl_id.weight = 5

        # Assign logistic units to product packaging
        product_packaging_obj = self.env['product.packaging']
        self.product_pack_3 = product_packaging_obj.create(
            {'name': 'product pack 3 units',
             'product_tmpl_id': self.product.product_tmpl_id.id,
             'qty': 3.0,
             'list_price': 60.0,
             "weight": 1.2,
             })
        self.product_pack_6 = product_packaging_obj.create(
            {'name': 'product pack 6 units',
             'product_tmpl_id': self.product.product_tmpl_id.id,
             'qty': 6.0,
             'list_price': 90.0,
             "weight": 1.5,
             })

        self.sale_order_model = self.env['sale.order']
        self.partner_model = self.env['res.partner']
        self.partner1 = self.partner_model.create({'name': 'Partner1'})
        self.sale_order = self.sale_order_model.create({
            'partner_id': self.partner1.id,
            'order_policy': 'manual',
            'order_line': [(0, 0, {'product_id': self.product.id, })],
        })

    def test_sale_packaging_price(self):
        """Order line gets updated correctly."""
        # Using a 3 pack
        self.sale_order.order_line.product_uom_qty = 3
        self.sale_order.order_line.product_packaging = self.product_pack_3
        self.sale_order.order_line._onchange_product_packaging()
        self.assertEqual(self.sale_order.order_line.price_unit, 20)
        self.assertEqual(self.sale_order.order_line.packaging_weight, 16.2)

        # Using a 6 pack
        self.sale_order.order_line.product_packaging = self.product_pack_6
        self.sale_order.order_line._onchange_product_packaging()
        self.assertEqual(self.sale_order.order_line.price_unit, 30)
        self.assertEqual(self.sale_order.order_line.packaging_weight, 16.5)

    def test_onchange_price_list(self):
        """User is warned when pack price is not divisible by qty."""
        self.product_pack_6.list_price = 100
        res = self.product_pack_6._onchange_list_price()
        self.assertIn('warning', res)

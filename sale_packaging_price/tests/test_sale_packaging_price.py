# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.tests.common import TransactionCase


class TestSalePackagingPrice(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestSalePackagingPrice, self).setUp()
        self.product = self.env.ref('product.product_product_6')
        self.product.product_tmpl_id.lst_price = 10.0

        # Create logistic units
        product_ul_obj = self.env['product.ul']
        self.pack_3 = product_ul_obj.create({'name': 'pack 3 units',
                                             'type': 'box',
                                             'weight': 25.50})
        self.pack_6 = product_ul_obj.create({'name': 'pack 6 units',
                                             'type': 'box'})

        # Assign logistic units to product packaging
        product_packaging_obj = self.env['product.packaging']
        self.product_pack_3 = product_packaging_obj.create(
            {'name': 'product pack 3 units',
             'product_tmpl_id': self.product.product_tmpl_id.id,
             'ul': self.pack_3.id,
             'qty': 3.0,
             'list_price': 60.0,
             })
        self.product_pack_6 = product_packaging_obj.create(
            {'name': 'product pack 6 units',
             'product_tmpl_id': self.product.product_tmpl_id.id,
             'ul': self.pack_6.id,
             'qty': 6.0,
             'list_price': 90.0,
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
        res = self.sale_order.order_line.product_packaging_change(
            1, self.product.id, qty=3, uom=False,
            partner_id=self.sale_order.partner_id.id,
            packaging=self.product_pack_3.id, flag=False)
        price_unit = res['value']['price_unit']
        self.assertAlmostEqual(price_unit, 20.0)

        # Check package weight
        res = self.sale_order.order_line.product_packaging_change(
            1, self.product.id, qty=2, uom=False,
            partner_id=self.sale_order.partner_id.id,
            packaging=self.product_pack_3.id, flag=False)
        package_weight = res['value']['packaging_weight']
        self.assertAlmostEqual(package_weight, 25.5)

        res = self.sale_order.order_line.product_packaging_change(
            1, self.product.id, qty=6, uom=False,
            partner_id=self.sale_order.partner_id.id,
            packaging=self.product_pack_6.id, flag=False)
        price_unit = res['value']['price_unit']
        self.assertAlmostEqual(price_unit, 15.0)

        # Check values when delete package assigned
        res = self.sale_order.order_line.product_packaging_change(
            1, self.product.id, qty=6, uom=False,
            partner_id=self.sale_order.partner_id.id,
            packaging=False, flag=False)
        price_unit = res['value']['price_unit']
        package_weight = res['value']['packaging_weight']
        self.assertAlmostEqual(
            price_unit, self.product.product_tmpl_id.lst_price)
        self.assertAlmostEqual(package_weight, 0.0)

    def test_onchange_price_list(self):
        self.product_pack_6.list_price = 100
        res = self.product_pack_6._onchange_list_price()
        self.assertIn('warning', res)

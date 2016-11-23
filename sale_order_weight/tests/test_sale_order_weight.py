# -*- coding: utf-8 -*-
# Copyright 2016 Andrea Cometa - Apulia Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

import openerp.tests.common as common


class TestSaleOrderWeight(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderWeight, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line_model = self.env['sale.order.line']
        self.partner = self.env.ref('base.res_partner_3')
        order_vals = self.sale_order_model.onchange_partner_id(
            self.partner.id)['value']
        order_vals['partner_id'] = self.partner.id

        line_data = [
            (0, 0, {
                'product_id': self.env.ref('product.product_product_4').id,
                'name': 'product test 4',
                'product_uom_qty': 1.0,
                'product_uom': self.env.ref(
                    'product.product_product_4').uom_id.id,
                'price_unit': self.env.ref(
                    'product.product_product_4').lst_price,
            }),
            (0, 0, {
                'product_id': self.env.ref('product.product_product_5').id,
                'name': 'product test 5',
                'product_uom_qty': 2.0,
                'product_uom': self.env.ref(
                    'product.product_product_5').uom_id.id,
                'price_unit': self.env.ref(
                    'product.product_product_5').lst_price,
            }),
            (0, 0, {
                'product_id': self.env.ref('product.product_product_3').id,
                'name': 'product test 3',
                'product_uom_qty': 3.0,
                'product_uom': self.env.ref(
                    'product.product_product_3').uom_id.id,
                'price_unit': self.env.ref(
                    'product.product_product_3').lst_price,
            }),
        ]
        order_vals['order_line'] = line_data
        self.sale_order = self.sale_order_model.create(order_vals)

    def test_total_weight(self):
        # Change weight
        self.env.ref('product.product_product_3').weight = 2.0  # 3.0
        self.env.ref('product.product_product_4').weight = 10.0  # 1.0
        self.env.ref('product.product_product_5').weight = 1.0  # 2.0
        # check total weight
        self.assertEqual(self.sale_order.total_weight(), 18.0)

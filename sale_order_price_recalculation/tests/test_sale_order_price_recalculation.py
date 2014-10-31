# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestSaleOrderPriceRecalculation(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderPriceRecalculation, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line_model = self.env['sale.order.line']
        self.partner = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_product_4')
        order_vals = self.sale_order_model.onchange_partner_id(
            self.partner.id)['value']
        order_vals['partner_id'] = self.partner.id
        self.sale_order = self.sale_order_model.create(order_vals)
        self.product.uos_id = self.env.ref('product.product_uom_kgm')
        self.product.uos_coeff = 12.0
        line_vals = {
            'product_id': self.product.id,
            'name': self.product.name,
            'product_uom_qty': 1.0,
            'product_uom': self.product.uom_id.id,
            'product_uos_qty': 12.0,
            'product_uos': self.product.uos_id.id,
            'price_unit': self.product.lst_price,
            'order_id': self.sale_order.id,
        }
        self.sale_order_line = self.sale_order_line_model.create(line_vals)

    def test_price_recalculation(self):
        # Check current price
        self.assertEqual(
            self.sale_order_line.price_unit, self.product.lst_price)
        # Change price
        self.product.lst_price = 500
        # Launch recalculation
        self.sale_order.recalculate_prices()
        # Check if the price has been updated
        self.assertEqual(
            self.sale_order_line.price_unit, self.product.lst_price)
        # Check if quantities have changed
        self.assertEqual(self.sale_order_line.product_uom_qty, 1.0)
        self.assertEqual(self.sale_order_line.product_uos_qty, 12.0)

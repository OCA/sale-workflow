# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestSaleLastPricePer_Partner(common.TransactionCase):

    def create_sale_orders(self):
        sale_obj1 = self.env['sale.order']
        partner_values = {'name': 'Imperator Caius Julius Caesar Divus'}
        partner = self.env['res.partner'].create(partner_values)
        product_values = {'name': 'Bread',
                          'list_price': 5, }
        product = self.env['product.product'].create(product_values)
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        values = {
            'partner_id': partner.id,
            'date_order': '2017-06-15 07:16:27',
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom': self.product_uom_unit.id,
                'price_unit': product.list_price,
                'product_uom_qty': 1})],
        }
        return sale_obj1.create(values)

    def test_first_sale(self):
        sale_obj1 = self.create_sale_orders()
        self.assertEqual(sale_obj1.order_line[0].last_sale_price, 0)
        self.assertEqual(sale_obj1.order_line[0].last_sale_qty, 0)

    def test_confirmed_sale(self):
        sale_obj1 = self.create_sale_orders()
        sale_obj1.action_confirm()
        self.assertEqual(sale_obj1.order_line[0].last_sale_price, 5)
        self.assertEqual(sale_obj1.order_line[0].last_sale_qty, 1)

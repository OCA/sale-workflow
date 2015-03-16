# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import exceptions
from openerp.tests import common


class TestSaleOrder(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        payment_term_model = self.env['account.payment.term']
        self.payment_term = payment_term_model.create({'name': 'test'})
        self.env['account.payment.term.line'].create({
            'payment_id': self.payment_term.id,
            'value': 'procent',
            'value_amount': 0.3333,
            'days': 10,
            'interest_rate': 0.0,
        })
        self.env['account.payment.term.line'].create({
            'payment_id': self.payment_term.id,
            'value': 'procent',
            'value_amount': 0.3333,
            'days': 40,
            'interest_rate': 0.041666,
        })
        self.env['account.payment.term.line'].create({
            'payment_id': self.payment_term.id,
            'value': 'balance',
            'days': 70,
            'interest_rate': 0.041666,
        })

    def test_interest(self):
        product1 = self.env.ref('product.product_product_7')
        product2 = self.env.ref('product.product_product_9')
        line1_values = {
            'product_id': product1.id,
            'product_uom_qty': 1,
            'product_uom': product1.uom_id.id,
            'price_unit': 50,
        }
        line2_values = {
            'product_id': product2.id,
            'product_uom_qty': 2,
            'product_uom': product1.uom_id.id,
            'price_unit': 100,
        }
        sale = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'payment_term': self.payment_term.id,
            'order_line': [(0, 0, line1_values), (0, 0, line2_values)],
        })
        self.assertEqual(len(sale.order_line), 3)
        interest_lines = set()
        for line in sale.order_line:
            if line.interest_line:
                interest_lines.add(line)
        self.assertEqual(len(interest_lines), 1)
        line = interest_lines.pop()
        self.assertAlmostEqual(line.price_subtotal, 3.82)
        self.assertAlmostEqual(sale.amount_total, 253.82)
        sale.check_interest_line()  # no error

    def test_interest_change_line(self):
        product1 = self.env.ref('product.product_product_7')
        product2 = self.env.ref('product.product_product_9')
        sale = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'payment_term': self.payment_term.id,
        })
        self.env['sale.order.line'].create({
            'product_id': product1.id,
            'product_uom_qty': 1,
            'product_uom': product1.uom_id.id,
            'price_unit': 50,
            'order_id': sale.id,
        })
        line2 = self.env['sale.order.line'].create({
            'product_id': product2.id,
            'product_uom_qty': 2,
            'product_uom': product1.uom_id.id,
            'price_unit': 100,
            'order_id': sale.id,
        })
        self.assertEqual(len(sale.order_line), 2)
        with self.assertRaises(exceptions.Warning):
            sale.check_interest_line()

        sale.update_interest_line()
        sale.check_interest_line()  # no error
        interest_line = sale._get_interest_line()
        self.assertAlmostEqual(interest_line.price_subtotal, 3.82)
        line2.product_uom_qty = 3

        sale.update_interest_line()
        sale.check_interest_line()  # no error
        self.assertAlmostEqual(interest_line.price_subtotal, 5.35)

        sale.payment_term = self.env.ref('account.account_payment_term_15days')
        interest_line = sale._get_interest_line()
        self.assertFalse(interest_line)

    def test_interest_with_tax(self):
        product1 = self.env.ref('product.product_product_7')
        product2 = self.env.ref('product.product_product_9')
        product_interest = self.env.ref('sale_payment_term_interest.'
                                        'product_product_sale_order_interest')
        tax = self.env['account.tax'].create({
            'name': 'Percent tax',
            'type': 'percent',
            'amount': '0.1',
        })
        product_interest.taxes_id = [(6, 0, [tax.id])]
        line1_values = {
            'product_id': product1.id,
            'product_uom_qty': 1,
            'product_uom': product1.uom_id.id,
            'price_unit': 50,
            'tax_id': [(6, 0, [tax.id])],
        }
        line2_values = {
            'product_id': product2.id,
            'product_uom_qty': 2,
            'product_uom': product1.uom_id.id,
            'price_unit': 100,
            'tax_id': [(6, 0, [tax.id])],
        }
        sale = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'payment_term': self.payment_term.id,
            'order_line': [(0, 0, line1_values), (0, 0, line2_values)],
        })
        self.assertEqual(len(sale.order_line), 3)
        interest_line = sale._get_interest_line()
        self.assertAlmostEqual(interest_line.price_subtotal, 4.2)
        self.assertAlmostEqual(sale.amount_total, 279.2)
        sale.check_interest_line()  # no error

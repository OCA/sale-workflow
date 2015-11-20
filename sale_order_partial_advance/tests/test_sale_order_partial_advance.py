# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of sale_order_partial_advance,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     sale_order_partial_advance is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     sale_order_partial_advance is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with sale_order_partial_advance.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tests import common as test_common
from uuid import uuid4


class TestSaleOrderPartialAdvance(test_common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderPartialAdvance, self).setUp()
        self.so_obj = self.env['sale.order']
        self.data_obj = self.env['ir.model.data']
        self.partner_id = self.env['res.partner'].create(
            {'name': '%s' % uuid4()})
        product1 = self.data_obj.get_object_reference('product',
                                                      'product_product_28')[1]
        product2 = self.data_obj.get_object_reference('product',
                                                      'product_product_29')[1]
        self.order_lines = [
            (0, 0, {'product_id': product1,
                    'name': 'Test',
                    'product_uom_qty': 10.0,
                    'price_unit': 100
                    }),
            (0, 0, {'product_id': product2,
                    'name': 'Test',
                    'product_uom_qty': 5.0,
                    'price_unit': 120
                    })]

    def test_sale_order_partial_advance(self):
        '''
            Test scenario
            - Create a sale order with 2 lines
            - Confirm the sale order
            - Invoice an advance of 500
            - Invoice the first order line and use 200 from the advance
            - Invoice the balance, the 300 remaining from the initial
              advance should be used automatically
        '''
        # ----------------------------------------------
        # Create and confirm a sale order with 2 lines
        # ----------------------------------------------
        vals = {
            'partner_id': self.partner_id.id,
            'order_line': self.order_lines,
        }
        order = self.so_obj.create(vals)
        self.assertEqual(order.amount_total, 1600.0)
        order.action_button_confirm()

        # ----------------------------------------------
        #    Invoice a deposit of 500.0
        # ----------------------------------------------
        adv_wizard = self.env['sale.advance.payment.inv'].create(
            {'advance_payment_method': 'fixed',
             'amount': 500.0,
             })
        adv_wizard.with_context(active_ids=[order.id]).create_invoices()
        self.assertTrue(order.invoice_ids)
        self.assertEqual(order.advance_amount, 500.0)
        self.assertEqual(order.advance_amount_available, 500.0)
        self.assertEqual(order.advance_amount_used, 0.0)

        # ---------------------------------------------------------------------
        #    Invoice the first sale order line and consume 200.0 from
        #    the deposit
        # ---------------------------------------------------------------------
        wizard = self.env['sale.order.line.make.invoice'].with_context(
            active_ids=[order.order_line[0].id]).create({})
        wizard.order_ids[0].advance_amount_to_use = 200.0
        res = wizard.with_context(open_invoices=True).make_invoices()
        invoice = self.env['account.invoice'].browse(res['res_id'])
        self.assertEqual(invoice.amount_total, 800.0)
        self.assertEqual(order.advance_amount, 500.0)
        self.assertEqual(order.advance_amount_available, 300.0)
        self.assertEqual(order.advance_amount_used, 200.0)

        # ----------------------------------------------
        #    Invoice the remaining balance
        # ----------------------------------------------
        adv_wizar = self.env['sale.advance.payment.inv'].create(
            {'advance_payment_method': 'all',
             })
        res = adv_wizar.with_context(active_ids=[order.id],
                                     open_invoices=True).create_invoices()
        invoice = self.env['account.invoice'].browse(res['res_id'])
        self.assertEqual(invoice.amount_total, 300.0)
        self.assertEqual(order.advance_amount, 500.0)
        self.assertEqual(order.advance_amount_available, 0.0)
        self.assertEqual(order.advance_amount_used, 500.0)

    def test_sale_order_partial_advance_all_lines(self):
        '''
            Test scenario
            - Create a sale order with 2 lines
            - Confirm the sale order
            - Invoice an advance
            - Invoice the 2 order lines at the same time, the whole advance
              amount should be used
        '''
        # ----------------------------------------------
        # Create and confirm a sale order with 2 lines
        # ----------------------------------------------
        vals = {
            'partner_id': self.partner_id.id,
            'order_line': self.order_lines,
        }
        order = self.so_obj.create(vals)
        self.assertEqual(order.amount_total, 1600.0)
        order.action_button_confirm()

        # ----------------------------------------------
        #    Invoice a deposit of 500.0
        # ----------------------------------------------
        adv_wizard = self.env['sale.advance.payment.inv'].create(
            {'advance_payment_method': 'fixed',
             'amount': 500.0,
             })
        adv_wizard.with_context(active_ids=[order.id]).create_invoices()
        self.assertTrue(order.invoice_ids)
        self.assertEqual(order.advance_amount, 500.0)
        self.assertEqual(order.advance_amount_available, 500.0)
        self.assertEqual(order.advance_amount_used, 0.0)

        # ----------------------------------------------------------
        #    Invoice the 2 sale order line, the whole advance amount
        #    should be consumed
        # ----------------------------------------------
        wizard = self.env['sale.order.line.make.invoice'].with_context(
            active_ids=order.order_line.ids).create({})
        res = wizard.with_context(open_invoices=True).make_invoices()
        invoice = self.env['account.invoice'].browse(res['res_id'])
        self.assertEqual(invoice.amount_total, 1100.0)
        self.assertEqual(order.advance_amount, 500.0)
        self.assertEqual(order.advance_amount_available, 0.0)
        self.assertEqual(order.advance_amount_used, 500.0)

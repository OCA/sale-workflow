# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestSaleIsolatedQuotation(TransactionCase):

    def quotation_assertions(self):
        self.assertEqual(self.quotation.state, 'done')
        self.sale_order = self.quotation.order_id
        self.assertTrue(self.sale_order.is_order)
        self.assertEqual(self.sale_order.state, 'draft')
        self.assertEqual(self.sale_order.partner_id, self.partner)
        self.assertEqual(self.sale_order.quote_id, self.quotation)

    def test_quotation_convert_to_order(self):
        """
        - When quotation is converted to order
          - Status chagned to 'done'
          - New sale.order of is_order = True created
        - Quotation can refer to Order and Order can refer to Quotation
        """
        self.quotation.action_convert_to_order()
        self.quotation_assertions()

    def test_quotation_confirm_order(self):
        """
        When confirm order is called on a quotation we need to ensure
        that the quotation is converted to an order.
        :return:
        """
        self.quotation.action_confirm()
        self.quotation_assertions()

    def test_sale_confirm_order(self):
        """
        When a sales order is converted to an order we need to ensure that
        behaviour of sale module is unchanged
        """
        self.quotation.is_order = True
        self.quotation.action_confirm()
        self.assertFalse(self.quotation.quote_id)
        self.assertFalse(self.quotation.order_id)
        self.assertFalse(self.quotation.state in ('draft', 'sent', 'cancel'))

    def test_quotation_search(self):
        """
        Because the amendment to search is highly dependent on hardcoded
        upstream function we test fully for any change to its behaviour.
        """
        # At start of search both orders are in draft state.
        sale_obj = self.env['sale.order']
        search = sale_obj.search
        web_search = self.env['sale.order'].with_context(website_id=1).search
        orders = self.quotation + self.sale_order
        self.assertEqual(len(search([('id', '=', self.quotation.id)])), 1)
        # A typical backend search
        self.assertEqual(
            len(search([('id', 'in', orders.ids),
                       ('state', 'in', ['sent', 'cancel'])])), 0)
        self.assertEqual(
            len(web_search([('id', 'in', orders.ids),
                           ('state', 'in', ['sent', 'cancel'])])), 0)
        # Test sent state - 2 should appear in backend, only 1 in website
        orders.write({'state': 'sent'})
        self.assertEqual(
            len(search([('id', 'in', orders.ids),
                       ('state', 'in', ['sent', 'cancel'])])), 2)
        web_quotes = web_search([('id', 'in', orders.ids),
                                ('state', 'in', ['sent', 'cancel'])])
        self.assertEqual(len(web_quotes), 1)
        self.assertTrue(web_quotes.id == self.quotation.id)

        # Test sale, done state
        orders.action_confirm()
        self.assertEqual(
            len(search([('id', 'in', orders.ids),
                       ('state', 'in', ['sale', 'done'])])), 2)
        web_orders = web_search([('id', 'in', orders.ids),
                                ('state', 'in', ['sale', 'done'])])
        self.assertEqual(len(web_orders), 1)
        self.assertTrue(web_orders.id == self.sale_order.id)

    def setUp(self):
        super(TestSaleIsolatedQuotation, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        vals = {'partner_id': self.partner.id,
                'is_order': False}
        self.quotation = self.env['sale.order'].new(vals)
        vals.update({'is_order': True})
        self.sale_order = self.env['sale.order'].new(vals)

# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestSaleIsolatedQuotation(TransactionCase):

    def test_quotation_convert_to_order(self):
        """
        - When quotation is converted to order
          - Status chagned to 'done'
          - New sale.order of is_order = True created
        - Quotation can refer to Order and Order can refer to Quotation
        """
        self.quotation.action_convert_to_order()
        self.assertEqual(self.quotation.state, 'done')
        self.sale_order = self.quotation.order_id
        self.assertTrue(self.sale_order.is_order)
        self.assertEqual(self.sale_order.state, 'draft')
        self.assertEqual(self.sale_order.partner_id, self.partner)
        self.assertEqual(self.sale_order.quote_id, self.quotation)

    def setUp(self):
        super(TestSaleIsolatedQuotation, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        vals = {'partner_id': self.partner.id,
                'is_order': False,
                }
        self.quotation = self.env['sale.order'].create(vals)

# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp.tests.common import TransactionCase


class TestPartnerProspect(TransactionCase):

    def setUp(self):
        super(TestPartnerProspect, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.partner_model = self.env['res.partner']
        self.partner1 = self.partner_model.create({'name': 'Partner1'})
        self.partner2 = self.partner_model.create({'name': 'Partner2'})
        self.product = self.env.ref('product.product_product_4')
        self.sale_order_line_model = self.env['sale.order.line']
        self.sale_order_partner1 = self.sale_order_model.create({
            'partner_id': self.partner1.id,
            'order_policy': 'manual',
            'order_line': [(0, 0, {'product_id': self.product.id, })],
        })
        self.sale_order_partner1.action_button_confirm()
        self.sale_order_partner2 = self.sale_order_model.create({
            'partner_id': self.partner2.id,
            'order_policy': 'manual',
            'order_line': [(0, 0, {'product_id': self.product.id, })],
        })
        self.sale_order_partner2.action_quotation_send()

    def test_partner_prospect_check(self):
        self.assertFalse(self.partner1.prospect, 'Partner1 is a prospect')
        self.assertTrue(self.partner2.prospect, 'Partner2 is not a prospect')

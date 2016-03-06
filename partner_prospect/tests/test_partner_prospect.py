# -*- coding: utf-8 -*-
# (c) 2015 Esther Martin - AvanzOSC
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestPartnerProspect(TransactionCase):

    def setUp(self):
        super(TestPartnerProspect, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.partner_model = self.env['res.partner']
        self.invoice_model = self.env['account.invoice']
        self.partner1 = self.partner_model.create({
            'name': 'Partner1',
        })
        self.partner2 = self.partner_model.create({
            'name': 'Partner2',
            'parent_id': self.partner1.id,
        })
        self.partner3 = self.partner_model.create({
            'name': 'Partner3',
            'parent_id': self.partner1.id,
        })
        self.partner4 = self.partner_model.create({'name': 'Partner4'})
        self.product = self.env.ref('product.product_product_4')
        self.sale_order1 = self.sale_order_model.create({
            'partner_id': self.partner1.id,
            'order_policy': 'manual',
            'order_line': [(0, 0, {'product_id': self.product.id, })],
        })
        self.sale_order2 = self.sale_order_model.create({
            'partner_id': self.partner2.id,
            'order_policy': 'manual',
            'order_line': [(0, 0, {'product_id': self.product.id, })],
        })
        self.sale_order3 = self.sale_order_model.create({
            'partner_id': self.partner4.id,
            'order_policy': 'manual',
            'order_line': [(0, 0, {'product_id': self.product.id, })],
        })

    def test_partner_child_check(self):
        self.sale_order2.action_button_confirm()
        self.assertFalse(self.partner1.prospect, 'Partner1 is a prospect')
        self.assertFalse(self.partner2.prospect, 'Partner2 is a prospect')
        self.assertFalse(self.partner3.prospect, 'Partner3 is a prospect')

    def test_partner_parent_check(self):
        self.sale_order1.action_button_confirm()
        self.assertFalse(self.partner1.prospect, 'Partner1 is a prospect')
        self.assertFalse(self.partner2.prospect, 'Partner2 is a prospect')
        self.assertFalse(self.partner3.prospect, 'Partner3 is a prospect')

    def test_partner_prospect(self):
        self.assertTrue(self.partner4.prospect, 'Partner4 is not a prospect')
        self.sale_order3.action_button_confirm()
        self.assertFalse(self.partner4.prospect, 'Partner4 is a prospect')
        self.sale_order3.action_cancel()
        self.assertTrue(self.partner4.prospect, 'Partner4 is not a prospect')

    def test_partner_child_check_invoice(self):
        type = 'out_invoice'
        invoice_vals = self.invoice_model.onchange_partner_id(
            type, self.partner2.id)
        self.invoice_model.create({
            'partner_id': self.partner2.id,
            'type': type,
            'account_id': invoice_vals.get('value', {}).get('account_id'),
        })
        self.assertFalse(self.partner1.prospect, 'Partner1 is a prospect')
        self.assertFalse(self.partner2.prospect, 'Partner2 is a prospect')
        self.assertFalse(self.partner3.prospect, 'Partner3 is a prospect')

    def test_partner_parent_check_invoice(self):
        type = 'out_refund'
        invoice_vals = self.invoice_model.onchange_partner_id(
            type, self.partner1.id)
        self.invoice_model.create({
            'partner_id': self.partner1.id,
            'type': type,
            'account_id': invoice_vals.get('value', {}).get('account_id'),
        })
        self.assertFalse(self.partner1.prospect, 'Partner1 is a prospect')
        self.assertFalse(self.partner2.prospect, 'Partner2 is a prospect')
        self.assertFalse(self.partner3.prospect, 'Partner3 is a prospect')

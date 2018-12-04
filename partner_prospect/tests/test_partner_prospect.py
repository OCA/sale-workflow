# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


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
        self.partner4 = self.partner_model.create({
            'name': 'Partner4',
        })
        self.product = self.env.ref('product.product_product_4')
        self.sale_order1 = self.sale_order_model.create({
            'partner_id': self.partner1.id,
            'order_line': [(0, 0, {'product_id': self.product.id, })],
        })
        self.sale_order2 = self.sale_order_model.create({
            'partner_id': self.partner2.id,
            'order_line': [(0, 0, {'product_id': self.product.id, })],
        })
        self.sale_order3 = self.sale_order_model.create({
            'partner_id': self.partner4.id,
            'order_line': [(0, 0, {'product_id': self.product.id, })],
        })

    def test_partner_child_check(self):
        self.sale_order2.action_confirm()
        self.assertFalse(self.partner1.prospect, 'Partner1 is a prospect')
        self.assertFalse(self.partner2.prospect, 'Partner2 is a prospect')
        self.assertFalse(self.partner3.prospect, 'Partner3 is a prospect')

    def test_partner_parent_check(self):
        self.sale_order1.action_confirm()
        self.assertFalse(self.partner1.prospect, 'Partner1 is a prospect')
        self.assertFalse(self.partner2.prospect, 'Partner2 is a prospect')
        self.assertFalse(self.partner3.prospect, 'Partner3 is a prospect')

    def test_partner_prospect(self):
        self.assertTrue(self.partner4.prospect, 'Partner4 is not a prospect')
        self.sale_order3.action_confirm()
        self.assertFalse(self.partner4.prospect, 'Partner4 is a prospect')
        self.sale_order3.action_cancel()
        self.assertTrue(self.partner4.prospect, 'Partner4 is not a prospect')

    def test_partner_child_check_invoice(self):
        ttype = 'out_invoice'
        self.invoice_model.create({
            'partner_id': self.partner2.id,
            'type': ttype,
        })._onchange_partner_id()
        self.assertFalse(self.partner1.prospect, 'Partner1 is a prospect')
        self.assertFalse(self.partner2.prospect, 'Partner2 is a prospect')
        self.assertFalse(self.partner3.prospect, 'Partner3 is a prospect')

    def test_partner_parent_check_invoice(self):
        ttype = 'out_refund'
        self.invoice_model.create({
            'partner_id': self.partner1.id,
            'type': ttype,
        })._onchange_partner_id()
        self.assertFalse(self.partner1.prospect, 'Partner1 is a prospect')
        self.assertFalse(self.partner2.prospect, 'Partner2 is a prospect')
        self.assertFalse(self.partner3.prospect, 'Partner3 is a prospect')

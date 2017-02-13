# -*- coding: utf-8 -*-
# Copyright 2016 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp import fields


class TestSalePayment(TransactionCase):

    def setUp(self):
        super(TestSalePayment, self).setUp()
        sale_obj = self.env['sale.order']
        partner_values = {'name': 'Test Partner'}
        partner = self.env['res.partner'].create(partner_values)
        product_values = {'name': 'Product Test',
                          'list_price': 50,
                          'type': 'product'}
        product = self.env['product.product'].create(product_values)
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        values = {
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom': self.product_uom_unit.id,
                'price_unit': product.list_price,
                'product_uom_qty': 1})],
        }
        self.sale_order = sale_obj.create(values)

        journal_vals = {
            'name': 'Test Journal',
            'type': 'bank',
            'code': 'test code'
        }
        self.journal = self.env['account.journal'].create(journal_vals)

    def test_01_payment(self):
        """Check if payment is well generated."""
        payment_obj = self.env['account.payment']
        vals = payment_obj.with_context(
            active_id=self.sale_order.id, active_model='sale.order').\
            default_get([])
        vals['journal_id'] = self.journal.id
        payment = payment_obj.new(vals)
        payment._onchange_journal()
        vals = payment._convert_to_write(payment._cache)
        payment = payment_obj.create(vals)
        payment.post()
        self.assertEqual(self.sale_order.residual, 0.0)
        self.assertEqual(
            self.sale_order.amount_paid, self.sale_order.amount_total)
        self.assertEqual(len(self.sale_order.payment_ids), 1)

    def test_02_statement_payment(self):
        """Check if payment is well generated."""
        statement_obj = self.env['account.bank.statement']
        statement_line_obj = self.env['account.bank.statement.line']
        statement_vals = {
            'journal_id': self.journal.id,
            'date': fields.Date.today(),
        }
        statement = statement_obj.create(statement_vals)
        line_vals = {
            'date': fields.Date.today(),
            'name': 'test memo',
            'amount': 127,
            'sale_ids': [(6, 0, [self.sale_order.id])],
            'statement_id': statement.id,
        }
        statement_line = statement_line_obj.new(line_vals)
        statement_line.onchange_sale_ids()
        line_vals = statement_line._convert_to_write(statement_line._cache)
        st_line = statement_line_obj.create(line_vals)
        statement.write({'balance_end_real': 127})
        self.assertEqual(st_line.partner_id.name, 'Test Partner')
        self.assertTrue(st_line.account_id)
        statement.button_confirm_bank()
        self.assertTrue(st_line.journal_entry_ids)
        move_payment_line = st_line.journal_entry_ids.line_ids.filtered(
            lambda l: l.credit > 0)
        self.assertEqual(
            move_payment_line.sale_ids.name, self.sale_order.name)

# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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
##############################################################################

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.returns('account.move.line')
    def _get_payment(self):
        self.ensure_one()
        if self.type == "out_invoice" and self.sale_ids:
            return self.sale_ids[0].payment_ids
        return self.env['account.move.line'].browse()

    @api.multi
    def _can_be_reconciled(self):
        self.ensure_one()
        payments = self._get_payment()
        if not (payments and self.move_id):
            return False
        # Check currency
        company_currency = self.company_id.currency_id
        for payment in payments:
            currency = payment.currency_id or company_currency
            if currency != self.currency_id:
                return False
        return True

    @api.model
    def _get_sum_invoice_move_line(self, move_lines, invoice_type):
        if invoice_type in ['in_refund', 'out_invoice']:
            line_type = 'debit'
        else:
            line_type = 'credit'
        return self._get_sum_move_line(move_lines, line_type)

    @api.model
    def _get_sum_payment_move_line(self, move_lines, invoice_type):
        if invoice_type in ['in_refund', 'out_invoice']:
            line_type = 'credit'
        else:
            line_type = 'debit'
        return self._get_sum_move_line(move_lines, line_type)

    @api.model
    def _get_sum_move_line(self, move_lines, line_type):
        res = {
            'max_date': False,
            'lines': self.env['account.move.line'].browse(),
            'total_amount': 0,
            'total_amount_currency': 0,
        }
        for move_line in move_lines:
            if move_line[line_type] > 0 and not move_line.reconcile_id:
                if move_line.date > res['max_date']:
                    res['max_date'] = move_line.date
                res['lines'] += move_line
                res['total_amount'] += move_line[line_type]
                res['total_amount_currency'] += move_line.amount_currency
        return res

    @api.multi
    def _prepare_write_off(self, res_invoice, res_payment):
        self.ensure_one()
        if res_invoice['total_amount'] - res_payment['total_amount'] > 0:
            writeoff_type = 'expense'
        else:
            writeoff_type = 'income'
        writeoff_info = self.company_id.get_write_off_information
        account_id, journal_id = writeoff_info('exchange', writeoff_type)
        max_date = max(res_invoice['max_date'], res_payment['max_date'])
        ctx_vals = {'p_date': max_date}
        period_model = self.env['account.period'].with_context(**ctx_vals)
        period = period_model.find(max_date)[0]
        return {
            'type': 'auto',
            'writeoff_acc_id': account_id,
            'writeoff_period_id': period.id,
            'writeoff_journal_id': journal_id,
            'context_vals': ctx_vals,
        }

    @api.multi
    def _lines_can_be_reconciled(self, lines):
        self.ensure_one()
        if not lines:
            return False
        # Check that all partners and accounts are the same
        first_partner = lines[0].partner_id
        first_account = lines[0].account_id
        for line in lines:
            if (line.account_id.type in ('receivable', 'payable') and
                    line.partner_id != first_partner):
                return False
            if line.account_id != first_account:
                return False
        return True

    @api.multi
    def _reconcile_invoice(self):
        self.ensure_one()
        company_currency = self.company_id.currency_id
        currency = self.currency_id
        use_currency = currency != company_currency
        if self._can_be_reconciled():
            payment_move_lines = self._get_payment()
            res_payment = self._get_sum_payment_move_line(payment_move_lines,
                                                          self.type)
            res_invoice = self._get_sum_invoice_move_line(self.move_id.line_id,
                                                          self.type)
            lines = res_invoice['lines'] + res_payment['lines']
            if not self._lines_can_be_reconciled(lines):
                return
            if not use_currency:
                balance = abs(res_invoice['total_amount'] -
                              res_payment['total_amount'])
                if lines and currency.is_zero(balance):
                    lines.reconcile()
            else:
                balance = abs(res_invoice['total_amount_currency'] -
                              res_payment['total_amount_currency'])
                if lines and currency.is_zero(balance):
                    kwargs = self._prepare_write_off(res_invoice, res_payment)
                    ctx_vals = kwargs.pop('context_vals')
                    lines.with_context(**ctx_vals).reconcile(**kwargs)

    @api.multi
    def reconcile_invoice(self):
        """ Simple method to reconcile the invoice with the payment
        generated on the sale order """
        for invoice in self:
            invoice._reconcile_invoice()
        return True

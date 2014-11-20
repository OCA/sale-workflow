# -*- coding: utf-8 -*-
###############################################################################
#
#   sale_automatic_workflow for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#   Copyright Camptocamp SA 2013 (Guewen Baconnier)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp.osv import fields, orm


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'workflow_process_id': fields.many2one('sale.workflow.process',
                                               string='Sale Workflow Process'),
        # TODO propose a merge to add this field by default in acount module
        'sale_ids': fields.many2many('sale.order', 'sale_order_invoice_rel',
                                     'invoice_id', 'order_id',
                                     string='Sale Orders')
    }

    def _get_payment(self, cr, uid, invoice, context=None):
        if invoice.type == "out_invoice" and invoice.sale_ids:
            return invoice.sale_ids[0].payment_ids
        return []

    def _can_be_reconciled(self, cr, uid, invoice, context=None):
        payments = self._get_payment(cr, uid, invoice, context=context)
        if not (payments and invoice.move_id):
            return False
        # Check currency
        company_currency_id = invoice.company_id.currency_id.id
        for payment in payments:
            currency_id = payment.currency_id.id or company_currency_id
            if currency_id != invoice.currency_id.id:
                return False
        return True

    def _get_sum_invoice_move_line(self, cr, uid, move_lines,
                                   invoice_type, context=None):
        if invoice_type in ['in_refund', 'out_invoice']:
            line_type = 'debit'
        else:
            line_type = 'credit'
        return self._get_sum_move_line(cr, uid, move_lines,
                                       line_type, context=None)

    def _get_sum_payment_move_line(self, cr, uid, move_lines,
                                   invoice_type, context=None):
        if invoice_type in ['in_refund', 'out_invoice']:
            line_type = 'credit'
        else:
            line_type = 'debit'
        return self._get_sum_move_line(cr, uid, move_lines,
                                       line_type, context=None)

    def _get_sum_move_line(self, cr, uid, move_lines, line_type, context=None):
        res = {
            'max_date': False,
            'line_ids': [],
            'total_amount': 0,
            'total_amount_currency': 0,
        }
        for move_line in move_lines:
            if move_line[line_type] > 0:
                if move_line.date > res['max_date']:
                    res['max_date'] = move_line.date
                res['line_ids'].append(move_line.id)
                res['total_amount'] += move_line[line_type]
                res['total_amount_currency'] += move_line.amount_currency
        return res

    def _prepare_write_off(self, cr, uid, invoice, res_invoice, res_payment,
                           context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        if res_invoice['total_amount'] - res_payment['total_amount'] > 0:
            writeoff_type = 'expense'
        else:
            writeoff_type = 'income'
        account_id, journal_id = invoice.company_id.\
            get_write_off_information('exchange', writeoff_type,
                                      context=context)
        max_date = max(res_invoice['max_date'], res_payment['max_date'])
        ctx['p_date'] = max_date
        period_obj = self.pool.get('account.period')
        period_id = period_obj.find(cr, uid, max_date, context=context)[0]
        return {
            'type': 'auto',
            'writeoff_acc_id': account_id,
            'writeoff_period_id': period_id,
            'writeoff_journal_id': journal_id,
            'context': ctx,
        }

    def _reconcile_invoice(self, cr, uid, invoice, context=None):
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        is_zero = currency_obj.is_zero
        company_currency_id = invoice.company_id.currency_id.id
        currency = invoice.currency_id
        use_currency = currency.id != company_currency_id
        if self._can_be_reconciled(cr, uid, invoice, context=context):
            payment_move_lines = []
            payment_move_lines = self._get_payment(cr, uid, invoice,
                                                   context=context)
            res_payment = self._get_sum_payment_move_line(
                cr, uid, payment_move_lines, invoice.type, context=context)
            res_invoice = self._get_sum_invoice_move_line(
                cr, uid, invoice.move_id.line_id,
                invoice.type, context=context)
            line_ids = res_invoice['line_ids'] + res_payment['line_ids']
            if not use_currency:
                balance = abs(res_invoice['total_amount'] -
                              res_payment['total_amount'])
                if line_ids and is_zero(cr, uid, currency, balance):
                    move_line_obj.reconcile(cr, uid, line_ids, context=context)
            else:
                balance = abs(res_invoice['total_amount_currency'] -
                              res_payment['total_amount_currency'])
                if line_ids and is_zero(cr, uid, currency, balance):
                    kwargs = self._prepare_write_off(cr, uid,
                                                     invoice,
                                                     res_invoice,
                                                     res_payment,
                                                     context=context)
                    move_line_obj.reconcile(cr, uid, line_ids, **kwargs)

    def reconcile_invoice(self, cr, uid, ids, context=None):
        """ Simple method to reconcile the invoice with the payment
        generated on the sale order """
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        for invoice in self.browse(cr, uid, ids, context=context):
            self._reconcile_invoice(cr, uid, invoice, context=context)
        return True

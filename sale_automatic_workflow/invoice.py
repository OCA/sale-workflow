# -*- coding: utf-8 -*-
###############################################################################
#
#   sale_automatic_workflow for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
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
from openerp.osv.orm import Model
from openerp.osv import fields

class account_invoice(Model):
    _inherit = "account.invoice"
    _columns = {
        'workflow_process_id':fields.many2one('sale.workflow.process', 'Sale Workflow Process'),
        #TODO propose a merge to add this field by default in acount module
        'sale_ids': fields.many2many('sale.order', 'sale_order_invoice_rel', 'invoice_id', 'order_id', 'Sale Orders')
    }

    def _can_be_reconciled(self, cr, uid, invoice, context=None):
        if not (invoice.sale_ids and invoice.sale_ids[0].payment_id and invoice.move_id):
            return False
        #Check currency
        for move in invoice.sale_ids[0].payment_id.move_ids:
            if (move.currency_id.id or invoice.company_id.currency_id.id) != invoice.currency_id.id:
                return False
        return True

    def _get_sum_invoice_move_line(self, cr, uid, move_lines, context=None):
        return self._get_sum_move_line(cr, uid, move_lines, 'debit', context=None)

    def _get_sum_payment_move_line(self, cr, uid, move_lines, context=None):
        return self._get_sum_move_line(cr, uid, move_lines, 'credit', context=None)

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

    def _prepare_write_off(self, cr, uid, invoice, res_invoice, res_payment, context=None):
        if not context:
            context = {}
        ctx = context.copy()
        if res_invoice['total_amount'] - res_payment['total_amount'] > 0:
            writeoff_type = 'expense'
        else:
            writeoff_type = 'income'
        account_id, journal_id = invoice.company_id.\
            get_write_off_information('exchange', writeoff_type, context=context)
        max_date = max(res_invoice['max_date'], res_payment['max_date'])
        ctx['p_date'] = max_date
        period_id = self.pool.get('account.period').find(cr, uid, max_date, context=context)[0]
        return {
            'type': 'auto',
            'writeoff_acc_id': account_id,
            'writeoff_period_id': period_id,
            'writeoff_journal_id': journal_id,
            'context': ctx,
        }

    def reconcile_invoice(self, cr, uid, ids, context=None):
        """
        Simple method to reconcile the invoice with the payment generated on the sale order
        """
        if not context:
            context={}
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        obj_move_line = self.pool.get('account.move.line')
        for invoice in self.browse(cr, uid, ids, context=context):
            use_currency = invoice.currency_id.id != invoice.company_id.currency_id.id
            if self._can_be_reconciled(cr, uid, invoice, context=context):
                payment_move_line = []
                for payment in invoice.sale_ids[0].payment_ids:
                    payment_move_line += payment.move_ids
                res_payment = self._get_sum_payment_move_line(cr, uid, payment_move_line, context=context)
                res_invoice = self._get_sum_invoice_move_line(cr, uid, invoice.move_id.line_id, context=context)
                line_ids = res_invoice['line_ids'] + res_payment['line_ids']
                if not use_currency:
                    balance = abs(res_invoice['total_amount']-res_payment['total_amount'])
                    if line_ids and not round(balance, precision):
                        obj_move_line.reconcile(cr, uid, line_ids, context=context)
                else:
                    balance = abs(res_invoice['total_amount_currency']-res_payment['total_amount_currency'])
                    if line_ids and not round(balance, precision):
                        kwargs = self._prepare_write_off(cr, uid, invoice, res_invoice, res_payment, context=context)
                        obj_move_line.reconcile(cr, uid, line_ids, **kwargs)
        return True

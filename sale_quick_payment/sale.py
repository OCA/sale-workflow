# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#    Copyright 2013 Camptocamp SA (Guewen Baconnier)
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

from openerp.osv import orm, fields, osv
from openerp.tools.translate import _
from collections import Iterable
import decimal_precision as dp


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _get_order_from_move(self, cr, uid, ids, context=None):
        result = set()
        move_obj = self.pool.get('account.move')
        for move in move_obj.browse(cr, uid, ids, context=context):
            for order in move.order_ids:
                result.add(order.id)
        return list(result)

    def _get_order_from_line(self, cr, uid, ids, context=None):
        so_obj = self.pool.get('sale.order')
        return so_obj._get_order(cr, uid, ids, context=context)

    def _amount_residual(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            amount = order.amount_total
            for move in order.payment_ids:
                amount -= move.amount
            res[order.id] = amount
        return res

    _columns = {
        'payment_ids': fields.many2many('account.move',
                                        string='Payments Entries'),
        'payment_method_id': fields.many2one('payment.method',
                                             'Payment Method',
                                             ondelete='restrict'),
        'residual': fields.function(
            _amount_residual,
            digits_compute=dp.get_precision('Account'),
            string='Balance',
            store=False),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['payment_ids'] = False
        return super(sale_order, self).copy(cr, uid, id,
                                            default, context=context)

    def pay_sale_order(self, cr, uid, sale_id, journal_id,
                       amount, date, context=None):
        """ Generate move lines entries to pay the sale order. """
        if isinstance(sale_id, Iterable):
            assert len(sale_id) == 1, "one sale order at a time can be paid"
            sale_id = sale_id[0]

        move_obj = self.pool.get('account.move')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')

        sale = self.browse(cr, uid, sale_id, context=context)
        journal = journal_obj.browse(cr, uid, journal_id, context=context)
        period_id = period_obj.find(cr, uid, dt=date, context=context)[0]
        period = period_obj.browse(cr, uid, period_id, context=context)
        move_name = self._get_payment_move_name(cr, uid, journal,
                                                period, context=context)
        move_vals = self._prepare_payment_move(cr, uid, move_name, sale,
                                               journal, period, date,
                                               context=context)
        move_lines = self._prepare_payment_move_line(cr, uid, move_name, sale,
                                                     journal, period, amount,
                                                     date, context=context)

        move_vals['line_id'] = [(0, 0, line) for line in move_lines]
        move_obj.create(cr, uid, move_vals, context=context)
        return True

    def _get_payment_move_name(self, cr, uid, journal, period, context=None):
        seq_obj = self.pool.get('ir.sequence')
        sequence = journal.sequence_id

        if not sequence:
            raise osv.except_osv(
                _('Configuration Error'),
                _('Please define a sequence on the journal %s.') %
                journal.name)
        if not sequence.active:
            raise osv.except_osv(
                _('Configuration Error'),
                _('Please activate the sequence of the journal %s.') %
                journal.name)

        ctx = context.copy()
        ctx['fiscalyear_id'] = period.fiscalyear_id.id
        name = seq_obj.next_by_id(cr, uid, sequence.id, context=ctx)
        return name

    def _prepare_payment_move(self, cr, uid, move_name, sale, journal,
                              period, date, context=None):
        return {'name': move_name,
                'journal_id': journal.id,
                'date': date,
                'ref': sale.name,
                'period_id': period.id,
                'order_ids': [(4, sale.id)],
                }

    def _prepare_payment_move_line(self, cr, uid, move_name, sale, journal,
                                   period, amount, date, context=None):
        """ """
        partner_obj = self.pool.get('res.partner')
        currency_obj = self.pool.get('res.currency')
        partner = partner_obj._find_accounting_partner(sale.partner_id)

        company = journal.company_id

        currency_id = False
        amount_currency = 0.0
        if journal.currency and journal.currency.id != company.currency_id.id:
            currency_id = journal.currency.id
            amount_currency, amount = (amount,
                                       currency_obj.compute(cr, uid,
                                                            currency_id,
                                                            company.currency_id.id,
                                                            amount,
                                                            context=context))

        # payment line (bank / cash)
        debit_line = {
            'name': move_name,
            'debit': amount,
            'credit': 0.0,
            'account_id': journal.default_credit_account_id.id,
            'journal_id': journal.id,
            'period_id': period.id,
            'partner_id': partner.id,
            'date': date,
            'amount_currency': amount_currency,
            'currency_id': currency_id,
        }

        # payment line (receivable)
        credit_line = {
            'name': move_name,
            'debit': 0.0,
            'credit': amount,
            'account_id': partner.property_account_receivable.id,
            'journal_id': journal.id,
            'period_id': period.id,
            'partner_id': partner.id,
            'date': date,
            'amount_currency': -amount_currency,
            'currency_id': currency_id,
        }
        return debit_line, credit_line

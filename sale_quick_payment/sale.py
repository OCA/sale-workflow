# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   sale_quick_payment for OpenERP                                  #
#   Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.osv.osv import except_osv
import netsvc
from collections import Iterable
from openerp.tools.translate import _
import decimal_precision as dp

class sale_order(Model):
    _inherit = "sale.order"

    def _get_order_from_voucher(self, cr, uid, ids, context=None):
        result = []
        for voucher in self.pool.get('account.voucher').browse(cr, uid, ids, context=context):
            for order in voucher.order_ids:
                result.append(order.id)
        return list(set(result))

    def _get_order_from_line(self, cr, uid, ids, context=None):
        return self.pool.get('sale.order')._get_order(cr, uid, ids, context=context)

    def _amount_residual(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        #TODO add here the support of multi-currency payment if need
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = order.amount_total
            for payment in order.payment_ids:
                if payment.state == 'posted':
                    res[order.id] -= payment.amount
        return res

    _columns = {
        'payment_ids': fields.many2many('account.voucher', string='Payments'),
        'payment_method_id': fields.many2one('payment.method',
                                             'Payment Method',
                                             ondelete='restrict'),
        'residual': fields.function(_amount_residual, digits_compute=dp.get_precision('Account'), string='Balance',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'payment_ids'], 10),
                'sale.order.line': (_get_order_from_line, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 20),
                'account.voucher': (_get_order_from_voucher, ['amount'], 30),
            },
            ),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'payment_ids': False,
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)

    def pay_sale_order(self, cr, uid, sale_id, journal_id, amount, date, context=None):
        """
        Generate a voucher for the payment

        It will try to match with the invoice of the order by
        matching the payment ref and the invoice origin.

        The invoice does not necessarily exists at this point, so if yes,
        it will be matched in the voucher, otherwise, the voucher won't
        have any invoice lines and the payment lines will be reconciled
        later with "auto-reconcile" if the option is used.

        """
        if isinstance(sale_id, Iterable):
            sale_id = sale_id[0]

        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        move_line_obj = self.pool.get('account.move.line')
        sale = self.browse(cr, uid, sale_id, context=context)

        journal = self.pool.get('account.journal').browse(
            cr, uid, journal_id, context=context)

        voucher_vals = {'reference': sale.name,
                        'journal_id': journal_id,
                        'period_id': self.pool.get('account.period').find(cr, uid, dt=date,
                                                                          context=context)[0],
                        'amount': amount,
                        'date': date,
                        'partner_id': sale.partner_id.id,
                        'account_id': journal.default_credit_account_id.id,
                        'currency_id': journal.company_id.currency_id.id,
                        'company_id': journal.company_id.id,
                        'type': 'receipt', }

        # Set the payment rate if currency are different
        if journal.currency.id and journal.company_id.currency_id.id != journal.currency.id:
            currency_id = journal.company_id.currency_id.id
            payment_rate_currency_id = journal.currency.id

            currency_obj = self.pool.get('res.currency')
            ctx= context.copy()
            ctx.update({'date': date})
            tmp = currency_obj.browse(cr, uid, payment_rate_currency_id, context=ctx).rate
            payment_rate = tmp / currency_obj.browse(cr, uid, currency_id, context=ctx).rate
            voucher_vals.update({
                'payment_rate_currency_id': payment_rate_currency_id,
                'payment_rate': payment_rate,
            })

        voucher_id = voucher_obj.create(cr, uid, voucher_vals, context=context)

        # call on change to search the invoice lines
        onchange_voucher = voucher_obj.onchange_partner_id(
            cr, uid, [],
            partner_id=sale.partner_id.id,
            journal_id=journal.id,
            amount=amount,
            currency_id=journal.company_id.currency_id.id,
            ttype='receipt',
            date=date,
            context=context)['value']

        # keep in the voucher only the move line of the
        # invoice (eventually) created for this order
        matching_line = {}
        if onchange_voucher.get('line_cr_ids'):
            voucher_lines = onchange_voucher['line_cr_ids']
            line_ids = [line['move_line_id'] for line in voucher_lines]
            matching_ids = [line.id for line
                            in move_line_obj.browse(
                                cr, uid, line_ids, context=context)
                            if line.ref == sale.name]
            matching_lines = [line for line
                              in voucher_lines
                              if line['move_line_id'] in matching_ids]
            if matching_lines:
                matching_line = matching_lines[0]
                matching_line.update({
                    'amount': amount,
                    'voucher_id': voucher_id,
                })

        if matching_line:
            voucher_line_obj.create(cr, uid, matching_line, context=context)

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
        sale.write({'payment_ids': [(4,voucher_id)]}, context=context)
        return True


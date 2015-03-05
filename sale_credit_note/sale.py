# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _get_credit_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            amount = 0
            for line in order.credit_line_ids:
                amount += line.amount
            res[order.id] = amount
        return res

    _columns = {
        'credit_line_ids': fields.one2many(
            'credit.line',
            'order_id',
            'Refund lines'),
        'total_credit_amount': fields.function(
            _get_credit_amount,
            type='float',
            digits_compute=dp.get_precision('Account'),
            string='Total credit amount'),
    }

    def get_payment_amount(self, cr, uid, ids, context=None):
        """
        Override function field method to take in account the refunded amount
        in the residual.
        """
        res = super(sale_order, self).get_payment_amount(
            cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            refunded_amount = 0
            for line in order.credit_line_ids:
                refunded_amount += line.amount
            res[order.id]['residual'] -= refunded_amount
        return res

    def get_credit_lines(self, cr, uid, ids, context=None):
        """
        Adds available credit lines on the sale order.
        """
        for order in self.browse(cr, uid, ids, context=context):
            lines = self._get_credit_lines(
                cr, uid, order.partner_id.id, order.residual, context=context)
            if lines:
                order.write({'credit_line_ids': lines})
        return True

    def _get_credit_lines(self, cr, uid, partner_id, max_amount, context=None):
        """
        Hook to get the available credit line in other modules.

        :rtype list of tuples
        """
        invoice_obj = self.pool['account.invoice']
        lines = []
        refund_ids = invoice_obj._search_available_refund(cr, uid, partner_id,
                                                          context=context)
        if not refund_ids:
            return lines
        for refund in invoice_obj.browse(cr, uid, refund_ids, context=context):
            refund_amount = invoice_obj._get_refund_amount(
                cr, uid, refund, context=context)
            if refund_amount <= 0:
                continue
            if refund_amount >= max_amount:
                lines.append((
                    0, 0, {'refund_id': refund.id, 'amount': max_amount}))
                break
            else:
                lines.append((
                    0, 0, {'refund_id': refund.id, 'amount': refund_amount}))
                max_amount -= refund_amount
        return lines


class credit_line(orm.Model):
    _name = "credit.line"

    _columns = {
        'order_id': fields.many2one('sale.order', 'Sale order', required=True),
        'amount': fields.float(
            'Amount',
            digits_compute=dp.get_precision('Account')),
        'refund_id': fields.many2one(
            'account.invoice',
            'Refund',
            required=True,
            domain=[('type', '=', 'out_refund'),
                    ('state', '!=', 'cancel'),
                    ('credit_note_amount', '!=', 0)],
            ),
        }

    def onchange_refund(
            self, cr, uid, ids, order_residual=False, refund_id=False,
            context=None):
        invoice_obj = self.pool['account.invoice']
        res = {'value': {}}
        if not refund_id:
            return res
        if order_residual <= 0:
            res['value']['refund_id'] = False
            res['warning'] = {
                'title': _('User Error'),
                'message': _("The order is totally paid or refunded, "
                             "you can't add a new refund line.")
            }
            return res
        refund = invoice_obj.browse(cr, uid, refund_id, context=context)
        refund_amount = invoice_obj._get_refund_amount(
            cr, uid, refund, context=context)
        if refund_amount <= 0:
            res['value']['refund_id'] = False
            res['warning'] = {
                'title': _('User Error'),
                'message': _("You can't use this refund on a new line, it is "
                             "totally refunded.")
            }
            return res
        if refund_amount > order_residual:
            res['value']['amount'] = order_residual
        else:
            res['value']['amount'] = refund_amount
        return res

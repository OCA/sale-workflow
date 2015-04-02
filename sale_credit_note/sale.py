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
            'sale.credit.line',
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

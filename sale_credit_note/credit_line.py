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


class sale_credit_line(orm.Model):
    _name = "sale.credit.line"
    _description = "Lines used to decrease the residual on sales from refunds."

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

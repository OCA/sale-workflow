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


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'credit_note_amount': fields.float(
            'Credit note amount',
            digits_compute=dp.get_precision('Account'),
            help="Amount available on sale orders to create a credit line"),
    }

    _defaults = {
        'credit_note_amount': 0
    }

    def _search_available_refund(self, cr, uid, partner_id, context=None):
        """
        Advanced search of refund (account.invoice).
        Can be overriden in ther modules.

        :rtype list of ids (account.invoice)
        """
        return self.search(
            cr, uid, [('type', '=', 'out_refund'),
                      ('state', '!=', 'cancel'),
                      ('credit_note_amount', '!=', 0),
                      '|', ('partner_id', '=', partner_id),
                      ('partner_id', 'child_of', partner_id)],
            order="date_invoice",
            context=context)

    def _get_refund_amount(self, cr, uid, refund, context=None):
        """
        Return the available credit amount of a refund (account.invoice).

        :rtype float
        """
        line_obj = self.pool['sale.redit.line']
        credit_line_ids = line_obj.search(
            cr, uid,
            [('refund_id', '=', refund.id),
             ('order_id.state', '!=', 'cancel')],
            context=context)
        refunded_amount = 0
        if credit_line_ids:
            for line in line_obj.browse(
                    cr, uid, credit_line_ids, context=context):
                refunded_amount += line.amount
        refund_total = refund.credit_note_amount - refunded_amount
        return refund_total

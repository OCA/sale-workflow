# -*- coding: utf-8 -*-
#
#
#   Copyright (C) 2013-TODAY Akretion <http://www.akretion.com>.
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
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
#

from openerp.osv import fields, orm


class SaleShop(orm.Model):
    _inherit = "sale.shop"

    _columns = {
        'journal_id': fields.many2one(
            'account.journal',
            'Sale Journal',
            domain=[('type', '=', 'sale')]),
    }


class SaleOrder(orm.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sale order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) lines: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        vals = super(SaleOrder, self)._prepare_invoice(
            cr, uid, order, lines, context=context)
        if order.shop_id.journal_id:
            vals['journal_id'] = order.shop_id.journal_id.id
        return vals

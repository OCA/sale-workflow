# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
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
###############################################################################

from openerp.osv import fields, orm
import decimal_precision as dp


class SaleOrderLine(orm.Model):
    _inherit = "sale.order.line"

    def _get_amount_line_tax(self, cr, uid, ids, field_name, arg,
                             context=None):
        order_obj = self.pool.get('sale.order')
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount_tax_line = order_obj._amount_line_tax(
                cr, uid, line, context=None)
            res[line.id] = {
                'price_subtotal_taxinc': amount_tax_line + line.price_subtotal,
                'vat_subtotal': amount_tax_line,
                }
        return res

    _columns = {
        'price_subtotal_taxinc': fields.function(
            _get_amount_line_tax,
            digits_compute=dp.get_precision('Sale Price'),
            string='Total Tax Inc',
            multi="tax_details"),
        'vat_subtotal': fields.function(
            _get_amount_line_tax,
            digits_compute=dp.get_precision('Sale Price'),
            string='Total VAT',
            multi="tax_details"),
    }

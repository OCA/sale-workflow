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


class AccountInvoiceLine(orm.Model):
    _inherit = "account.invoice.line"

    def _amount_line_tax_inc(self, cr, uid, ids, field_names, args,
                             context=None):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            cur = line.invoice_id.currency_id
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(
                cr, uid, line.invoice_line_tax_id, price, line.quantity,
                product=line.product_id,
                partner=line.invoice_id.partner_id)
            res[line.id] = {
                'price_subtotal_taxinc': cur_obj.round(
                    cr, uid, cur, taxes['total_included']),
                'vat_subtotal': cur_obj.round(
                    cr, uid, cur, (taxes['total_included'] - taxes['total'])),
                }
        return res

    _columns = {
        'price_subtotal_taxinc': fields.function(
            _amount_line_tax_inc,
            digits_compute=dp.get_precision('Sale Price'),
            string='Total Tax Inc',
            multi="tax_details"),
        'vat_subtotal': fields.function(
            _amount_line_tax_inc,
            digits_compute=dp.get_precision('Sale Price'),
            string='Total VAT',
            multi="tax_details"),
    }

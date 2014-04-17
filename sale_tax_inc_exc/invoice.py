# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP 
#   Copyright (C) 2011-2013 Akretion (http://www.akretion.com).
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

from invoice_sale import InvoiceSale, InvoiceSaleLine
from openerp.osv import fields, orm

class account_invoice(InvoiceSale):
    _inherit = "account.invoice"

    _columns = {
        'tax_inc' : fields.boolean('Tax Inc', help="Tic the box if you want to use unit price in taxe include"),
    }

class account_invoice_line(InvoiceSaleLine):
    _inherit = "account.invoice.line"

    #Try to use args and kwargs in order to have a module that do not break
    #time you inherit the onchange, code is not perfect because data can be
    #in args or kwargs depending of the other module installed
    #onchange = headache
    def product_id_change(self, cr, uid, ids, product_id, uom_id, *args, **kwargs):
        res = super(account_invoice_line, self).product_id_change(cr, uid, ids, product_id, uom_id, *args, **kwargs)
        if product_id: 
            if len(args) >= 3:
                invoice_type = args[2]
            else:
                invoice_type = kwargs.get('type', 'out_invoice')

            context = self._get_context_from_args_kwargs(args, kwargs)
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            if context is None:
                context = {}
            if context.get('tax_inc') and invoice_type in ('out_invoice', 'out_refund'):
                res['value'].update({'price_unit': product.list_price_tax_inc})
        return res


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

from openerp.osv import orm, fields
import decimal_precision as dp
from tools.translate import _
from invoice_sale import InvoiceSale, InvoiceSaleLine


class SaleOrder(InvoiceSale):
    _inherit = "sale.order"

    _columns = {
        'tax_inc' : fields.boolean(
            'Tax Inc',
            help="Tic the box if you want to use unit price in taxe include"),
    }

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        result = super(SaleOrder, self)._prepare_invoice(
            cr, uid, order, lines, context=context)
        result['tax_inc'] = order.tax_inc
        return result

    def onchange_shop_id(self, cr, uid, ids, *args, **kwargs):
        res = super(SaleOrder, self).onchange_shop_id(cr, uid, ids, *args, **kwargs)
        if len(args) >=1:
            shop_id = args[0]
        else:
            shop_id = kwargs.get('shop_id')
        if shop_id:
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
            res['value']['tax_inc'] = shop.tax_inc
        return res


class SaleOrderLine(InvoiceSaleLine):
    _inherit = "sale.order.line"


class SaleShop(orm.Model):
    _inherit = 'sale.shop'
    
    _columns = {
        'tax_inc' : fields.boolean('Tax Inc',
            help=("Tic the box if you want to use unit price in taxe include "
            "by default for this shop")),
    }

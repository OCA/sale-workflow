# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields, orm, osv
from tools.translate import _
import decimal_precision as dp


# we use TransientModel becuase this is just temporary search tool.
class ProductInquiry(orm.TransientModel):
    _name = "product.inquiry"
    _description = "Product Price Inquiry"

    def action_button_inquiry(self, cr, uid, ids, context=None):
        '''Do the price inquiry, generate the inquiry results.'''
        context = context or {}

        # use the first id.
        if ids and isinstance(ids, (list, tuple)):
            ids = ids[0]
        pricelist_obj = self.pool['product.pricelist']
        pil_obj = self.pool['product.inquiry.line']

        inquiry = self.browse(cr, uid, ids, context=context)
        pricelist_id = inquiry.pricelist_id.id
        product_id = inquiry.product_id.id
        qty = inquiry.qty

        qtylist = qty.strip(' ,').split(',')
        # remove the duplicated qty and null ones
        qtylist = [i for i in list(set(qtylist)) if i]

        for q in qtylist:
            if q.isdigit():
                price = pricelist_obj.price_get(
                    cr, uid, [pricelist_id], product_id, q)[pricelist_id]

                pil_obj.create(cr, uid, {
                    'product_id': product_id,
                    'pricelist_id': pricelist_id,
                    'qty': q,
                    'price_unit': price,
                    'inquiry_id': inquiry.id
                })
            else:
                raise osv.except_osv(
                    _('Error Input'),
                    _('Please check if your product qty is correct!\n'
                        'The right format of input is: '
                        'quantity1,quantity2,quantity3'))
        return True

    _columns = {
        'name': fields.char('Order Reference', size=64),
        'product_id': fields.many2one(
            'product.product', 'Product',
            domain=[('sale_ok', '=', True)], change_default=True),
        'pricelist_id': fields.many2one(
            'product.pricelist', 'Pricelist',
            domain=[('visible', '=', True)],
            required=True, help="Pricelist for current sales order."),
        'inquiry_line': fields.one2many(
            'product.inquiry.line', 'inquiry_id',
            'Inquiry Lines', readonly=True),
        'price_unit': fields.float(
            'Price Unit', required=True,
            digits_compute=dp.get_precision('Sale Price')
        ),
        'qty': fields.char(
            'Product Qty',
            help="Comma separated values of quantity. eg:100,1000,5000,10000",
            size=128, required=True,),
    }

    _defaults = {
        'qty': '0',
    }


class ProductInquiryLine(orm.TransientModel):
    _name = 'product.inquiry.line'
    _description = 'Product Inquiry Line'

    _columns = {
        'inquiry_id': fields.many2one(
            'product.inquiry', 'Inquiry Reference', required=True,
            ondelete='cascade', select=True, readonly=True
        ),
        'product_id': fields.many2one(
            'product.product', 'Product', domain=[('sale_ok', '=', True)],
            change_default=True),
        'pricelist_id': fields.many2one(
            'product.pricelist', 'Pricelist', required=True,
            help="Pricelist for current sales order."),
        'qty': fields.float(
            'Product Qty', required=True,
            digits_compute=dp.get_precision('Sale Price'),),
        'price_unit': fields.float(
            'Price Unit', required=True,
            digits_compute=dp.get_precision('Sale Price'),),
    }


class ProductPricelist(orm.Model):
    _name = "product.pricelist"
    _description = "Pricelist"
    _inherit = "product.pricelist"

    _columns = {
        "visible": fields.boolean(_("Visible in Pricelist inquiry")),
    }

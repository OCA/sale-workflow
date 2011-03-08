# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Akretion LTDA.
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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

from osv import fields, osv
from tools.translate import _
import netsvc

class sale_exception(osv.osv):
    _name = "sale.exception"
    _description = "Sale Exceptions"
    _columns = {
        'name': fields.char('Exception Name', size=64, required=True),
        'sale_order_ids': fields.many2many('sale.order', 'sale_order_exception_rel', 'exception_id', 'sale_order_id', 'Sale Orders'),
    }

sale_exception()

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'exceptions_ids': fields.many2many('sale.exception', 'sale_order_exception_rel', 'sale_order_id', 'exception_id', 'Exceptions'),
    }

    def __add_exception(self, cr, uid, exceptions_list, exception_name):
        ir_model_data_id = self.pool.get('ir.model.data').search(cr, uid, [('name', '=', exception_name)])[0]
        except_id = self.pool.get('ir.model.data').read(cr, uid, ir_model_data_id, ['res_id'])['res_id']
        if except_id not in exceptions_list:
            exceptions_list.append(except_id)

    def test_exceptions(self, cr, uid, ids, *args):
        for order in self.browse(cr, uid, ids, args):
            new_exceptions = []
            self.add_custom_order_exception(cr, uid, ids, order, new_exceptions, *args)
            self.write(cr, uid, [order.id], {'exceptions_ids': [(6, 0, new_exceptions)]})
            cr.commit()
        if len(new_exceptions) != 0:
            raise osv.except_osv(_('Order has errors!'), "\n".join(ex.name for ex in self.pool.get('sale.exception').browse(cr, uid, new_exceptions, *args)))
        return True

    def add_custom_order_exception(self, cr, uid, ids, order, exceptions, *args):
        self.detect_invalid_destination(cr, uid, order, exceptions)
        self.detect_no_zip(cr, uid, order, exceptions)
        for order_line in order.order_line:
            self.detect_wrong_product(cr, uid, order_line, exceptions)
            self.detect_not_enough_virtual_stock(cr, uid, order_line, exceptions)
        return exceptions

    def detect_invalid_destination(self, cr, uid, order, exceptions):
        if len(self.pool.get('delivery.grid').search(cr, uid, [('country_ids', 'ilike', "%%%s%%" % (order.partner_shipping_id.country_id.name,))])) > 0: #TODO may be add an extra condition on grid type/name
            self.__add_exception(cr, uid, exceptions, 'excep_invalid_location')

    def detect_no_zip(self, cr, uid, order, exceptions):
        if not order.partner_shipping_id.zip:
            self.__add_exception(cr, uid, exceptions, 'excep_no_zip')

    def detect_wrong_product(self, cr, uid, order_line, exceptions):
        if order_line.product_id and 'unknown' in order_line.product_id.name.lower() or not order_line.product_id:
            self.__add_exception(cr, uid, exceptions, 'excep_product')

    def detect_not_enough_virtual_stock(self, cr, uid, order_line, exceptions):
        if order_line.product_id and order_line.product_id.type == 'product' and order_line.product_id.virtual_available < order_line.product_uom_qty:
            self.__add_exception(cr, uid, exceptions, 'excep_no_stock')

sale_order()

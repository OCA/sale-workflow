# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Akretion LDTA (<http://www.akretion.com>).
#    @author Raphaël Valyi
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

from osv import fields,osv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import netsvc

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context)

        if product:
            context = {'lang': lang, 'partner_id': partner_id, 'qty': qty}
            product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
            if product_obj.is_direct_delivery_from_product:
                result['value'].update({'type': 'make_to_order', 'sale_flow': 'direct_delivery'})      
        return result

    def _purchase_order_line_id(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        po_line_class = self.pool.get('purchase.order.line')
        for order_line in self.browse(cr, uid, ids, context=context):
            po_line_ids = po_line_class.search(cr, uid, [('sale_order_line_id', '=', order_line.id), ('order_id.state', '!=', 'cancel')])
            result[order_line.id] = po_line_ids and po_line_ids[0] or False
        return result


    _columns = {
        'sale_flow': fields.selection([('normal', 'Normal'), ('direct_delivery', 'Drop Shipping'), ('direct_invoice', 'Direct Invoice/Indirect Delivery'), ('direct_invoice_and_delivery', 'Direct Invoice')], 'Sale Flow', help="Is this order tied to a sale order? How will it be delivered and invoiced then?"),
        'purchase_order_line_id': fields.function(_purchase_order_line_id, type='many2one', relation='purchase.order.line', string='Purchase Order Line'),
        'purchase_order_id': fields.related('purchase_order_line_id', 'order_id', type='many2one', relation='purchase.order', string='Purchase Order'),
        'purchase_order_state': fields.related('purchase_order_id', 'state', type='char', size=64, string='Purchase Order State'),
    }

    _defaults = {
        'sale_flow': 'normal',
    }

sale_order_line()


class sale_order(osv.osv):
    _inherit = "sale.order"

    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, context=None):
        res = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context)
        res['sale_order_line_id'] = line.id
        if line.sale_flow in ['direct_delivery', 'direct_invoice_and_delivery']:
            res['location_id'] = order.partner_id.property_stock_supplier.id
        return res

    #NOTE: the following code depends on a refactoring by Akretion that has been merged in OpenERP 6.1 (won't work un-pached on 6.0)
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        wf_service = netsvc.LocalService("workflow")
        res = {}
        normal_lines = []
        for line in order_lines:
            if line.sale_flow in ['direct_delivery', 'direct_invoice_and_delivery']:
                date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)

                proc_id = self.pool.get('procurement.order').create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, line, False, date_planned, context=context))
                line.write({'procurement_id': proc_id})
                wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
            else:
                normal_lines.append(line)
        res =  super(sale_order, self)._create_pickings_and_procurements(cr, uid, order, normal_lines, None, context)
        return res

sale_order()

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    _columns = {
        'sale_order_line_id': fields.many2one('sale.order.line', 'Sale Order Line'),
    }

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line_vals, context=None):
        if procurement.sale_order_line_id:
            warehouse_id = procurement.sale_order_line_id.order_id.shop_id.warehouse_id
            sale_flow = procurement.sale_order_line_id.sale_flow
            vals = self.pool.get('purchase.order').sale_flow_change(cr, uid, [], sale_flow, procurement.sale_order_line_id.order_id.id, warehouse_id.id)
            po_vals.update(vals.get('value', {}))
            po_vals.update({'sale_flow': sale_flow, 'sale_id': procurement.sale_order_line_id.order_id.id})
            line_vals.update({'sale_order_line_id': procurement.sale_order_line_id and procurement.sale_order_line_id.id or False})
        return super(procurement_order, self).create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context)

procurement_order()

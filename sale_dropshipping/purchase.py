# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Akretion LDTA (<http://www.akretion.com>).
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

from tools.translate import _
from osv import fields, osv
import netsvc
from datetime import datetime

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    _columns = {
        'sale_order_line_id': fields.many2one('sale.order.line', 'Sale Order Line'),
    }

purchase_order_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'sale_id': fields.many2one('sale.order', 'Related Sale Order'),
        'sale_flow': fields.selection([('normal', 'Normal'), ('direct_delivery', 'Drop Shipping'), ('direct_invoice', 'Direct Invoice/Indirect Delivery'), ('direct_invoice_and_delivery', 'Direct Invoice')], 'Sale Flow', help="Is this order tied to a sale order? How will it be delivered and invoiced then?"),
    }

    _defaults = {
        'sale_flow': 'normal',
    }

    def sale_flow_change(self, cr, uid, ids, sale_flow, sale_id, warehouse_id):
        if sale_id:
            partner_id = self.pool.get('sale.order').browse(cr, uid, sale_id).partner_id.id
            if sale_flow == 'direct_delivery': #TODO manual? in the 2 cases of direct invoice?
                return {'value': {'invoice_method': 'order', 'location_id': self.pool.get('res.partner').browse(cr, uid, partner_id).property_stock_customer.id, 'dest_address_id': self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery'])['delivery']}}
            elif sale_flow == 'direct_invoice':
                warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id)
                return {'value': {'invoice_method': 'picking', 'location_id': warehouse.lot_input_id.id, 'dest_address_id': self.pool.get('res.partner').address_get(cr, uid, [warehouse.company_id.partner_id.id], ['delivery'])['delivery']}}
            elif sale_flow == 'direct_invoice_and_delivery':
                return {'value': {'invoice_method': 'picking', 'location_id': self.pool.get('res.partner').browse(cr, uid, partner_id).property_stock_customer.id, 'dest_address_id': self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery'])['delivery']}}
            else:
                warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id)
                return {'value': {'location_id': warehouse.lot_input_id.id, 'dest_address_id': self.pool.get('res.partner').address_get(cr, uid, [warehouse.company_id.partner_id.id], ['delivery'])['delivery']}}
        else:
            return {}                

    def action_picking_create(self,cr, uid, ids, *args):
        res = super(purchase_order, self).action_picking_create(cr, uid, ids, *args)
        for purchase in self.browse(cr, uid, ids):
            if res: #TODO bad code inherited from OpenERP, see bug https://bugs.launchpad.net/openobject-addons/+bug/788789
                if purchase.sale_flow == 'direct_delivery':
                    if purchase.sale_id and purchase.sale_id.order_policy == 'picking':
                        invoice_control = '2binvoiced'
                    else:
                        invoice_control = 'none'
                    self.pool.get('stock.picking').write(cr, uid, res, {'type': 'out', 'invoice_state': invoice_control, 'sale_id': purchase.sale_id and purchase.sale_id.id})
                elif purchase.sale_flow == 'direct_invoice':
                    self.pool.get('stock.picking').write(cr, uid, res, {'invoice_state': 'none'})
                elif purchase.sale_flow == 'direct_invoice_and_delivery':
                    self.pool.get('stock.picking').write(cr, uid, res, {'type': 'out', 'invoice_state': 'none', 'sale_id': purchase.sale_id and purchase.sale_id.id})
        return res


purchase_order()


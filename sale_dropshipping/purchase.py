# -*- coding: utf-8 -*-
#
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
#
from openerp.osv import fields, orm


class purchase_order_line(orm.Model):
    _inherit = "purchase.order.line"

    _columns = {
        'sale_order_line_id': fields.many2one(
            'sale.order.line', 'Sale Order Line'),
    }


class purchase_order(orm.Model):
    _inherit = "purchase.order"

    _columns = {
        'analytic_account_id': fields.many2one(
            'account.analytic.account', 'Analytic Account'),
        'sale_id': fields.many2one('sale.order', 'Related Sale Order'),
        'sale_flow': fields.selection([
            ('normal', 'Normal'),
            ('direct_delivery', 'Drop Shipping'),
            ('direct_invoice', 'Direct Invoice/Indirect Delivery'),
            ('direct_invoice_and_delivery', 'Direct Invoice')],
            'Sale Flow',
            help="Is this order tied to a sale order?"
                 " How will it be delivered and invoiced then?"),
    }

    _defaults = {
        'sale_flow': 'normal',
    }

    def sale_flow_change(self, cr, uid, ids, sale_flow, sale_id,
                         warehouse_id, context=None):
        if sale_id:
            sale_obj = self.pool.get('sale.order')
            partner_obj = self.pool.get('res.partner')
            warehouse_obj = self.pool.get('stock.warehouse')
            sale = sale_obj.browse(cr, uid, sale_id, context=context)
            partner_id = sale.partner_id.id
            if sale_flow in ('direct_delivery', 'direct_invoice_and_delivery'):
                partner = partner_obj.browse(cr, uid, partner_id,
                                             context=context)
                address = partner.address_get(['delivery'])['delivery']
                vals = {'location_id': partner.property_stock_customer.id,
                        'dest_address_id': address}
                if sale_flow == 'direct_delivery':
                    vals['invoice_method'] = 'order'
                else:
                    vals['invoice_method'] = 'picking'
                return {'value': vals}
            else:
                warehouse = warehouse_obj.browse(cr, uid,
                                                 warehouse_id, context=context)
                company_partner = warehouse.company_id.partner_id
                address = company_partner.address_get(['delivery'])['delivery']
                vals = {'invoice_method': 'picking',
                        'location_id': warehouse.lot_input_id.id,
                        'dest_address_id': address}
                if sale_flow == 'direct_invoice':
                    vals['invoice_method'] = 'picking'
                return {'value': vals}
        return {}

    def action_picking_create(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).action_picking_create(
            cr, uid, ids, context=context)
        picking_obj = self.pool.get('stock.picking')
        for purchase in self.browse(cr, uid, ids, context=context):
            # TODO bad code inherited from OpenERP, see bug
            # https://bugs.launchpad.net/openobject-addons/+bug/788789
            if res:
                if purchase.sale_flow == 'direct_delivery':
                    if (
                        purchase.sale_id and
                        purchase.sale_id.order_policy == 'picking'
                    ):
                        invoice_control = '2binvoiced'
                    else:
                        invoice_control = 'none'
                    picking_obj.write(
                        cr, uid, res,
                        {'type': 'out',
                         'invoice_state': invoice_control,
                         'sale_id': purchase.sale_id and purchase.sale_id.id},
                        context=context)
                elif purchase.sale_flow == 'direct_invoice':
                    picking_obj.write(cr, uid, res,
                                      {'invoice_state': 'none'},
                                      context=context)
                elif purchase.sale_flow == 'direct_invoice_and_delivery':
                    picking_obj.write(
                        cr, uid, res,
                        {'type': 'out',
                         'invoice_state': 'none',
                         'sale_id': purchase.sale_id and purchase.sale_id.id},
                        context=context)
        return res

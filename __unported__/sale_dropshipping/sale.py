# -*- coding: utf-8 -*-
#
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
#
from openerp.osv import orm, fields
from openerp.tools.translate import _
import netsvc


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False,
                          lang=False, update_tax=True, date_order=False,
                          packaging=False,
                          fiscal_position=False, flag=False, context=None):

        result = super(
            sale_order_line, self).product_id_change(
                cr, uid, ids, pricelist,
                product, qty,
                uom, qty_uos, uos, name, partner_id, lang,
                update_tax, date_order, packaging,
                fiscal_position, flag, context)

        if product:
            context2 = {'lang': lang,
                        'partner_id': partner_id,
                        'qty': qty,
                        }
            product_obj = self.pool.get(
                'product.product').browse(cr, uid, product,
                                          context=context2)
            if product_obj.is_direct_delivery_from_product:
                result['value'].update({'type': 'make_to_order',
                                        'sale_flow': 'direct_delivery'})
        return result

    def _purchase_order_line_id(
        self, cr, uid, ids, field_name, arg, context=None
    ):
        result = {}
        po_line_class = self.pool.get('purchase.order.line')
        for order_line in self.browse(cr, uid, ids, context=context):
            po_line_ids = po_line_class.search(
                cr, uid,
                [
                    ('sale_order_line_id', '=', order_line.id),
                    ('order_id.state', '!=', 'cancel')
                ])
            result[order_line.id] = po_line_ids and po_line_ids[0] or False
        return result

    def onchange_sale_flow(self, cr, uid, ids, sale_flow, product_id,
                           context=None):
        """ Change type to make_to_order when sale_flow is direct_delivery """

        vals = {}
        if product_id:
            if sale_flow == 'direct_delivery':
                vals['type'] = 'make_to_order'
            else:
                product = self.pool['product.product'].browse(cr, uid,
                                                              product_id,
                                                              context=context)
                vals['type'] = product.procure_method
        return {'value': vals}

    _columns = {
        'sale_flow': fields.selection([
            ('normal', 'Normal'),
            ('direct_delivery', 'Drop Shipping'),
            ('direct_invoice', 'Direct Invoice/Indirect Delivery'),
            ('direct_invoice_and_delivery', 'Direct Invoice')],
            'Sale Flow',
            help="Is this order tied to a sale order?"
                 " How will it be delivered and invoiced then?"),

        'purchase_order_line_id': fields.function(
            _purchase_order_line_id,
            type='many2one',
            relation='purchase.order.line',
            string='Purchase Order Line'),

        'purchase_order_id': fields.related(
            'purchase_order_line_id',
            'order_id',
            type='many2one',
            relation='purchase.order',
            string='Purchase Order'),

        'purchase_order_state': fields.related(
            'purchase_order_id', 'state',
            type='char',
            size=64,
            string='Purchase Order State'),
    }

    _defaults = {
        'sale_flow': 'normal',
    }

sale_order_line()


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id,
                                        date_planned, context=None):
        res = super(
            sale_order, self)._prepare_order_line_procurement(
                cr, uid, order, line,
                move_id, date_planned,
                context)
        res['sale_order_line_id'] = line.id
        if line.sale_flow in [
            'direct_delivery', 'direct_invoice_and_delivery'
        ]:
            res['location_id'] = order.partner_id.property_stock_supplier.id
        return res

    def _create_procurements_direct_mto(self, cr, uid, order, order_lines,
                                        context=None):
        """ For make to order lines delivery as dropshipping, do not generate
        moves but only create a procurement order. """
        wf_service = netsvc.LocalService("workflow")
        proc_obj = self.pool.get('procurement.order')
        for line in order_lines:
            date_planned = self._get_date_planned(cr, uid, order,
                                                  line, order.date_order,
                                                  context=context)
            vals = self._prepare_order_line_procurement(
                cr, uid, order, line, False, date_planned, context=context)
            proc_id = proc_obj.create(cr, uid, vals, context=context)
            line.write({'procurement_id': proc_id})
            wf_service.trg_validate(uid, 'procurement.order',
                                    proc_id, 'button_confirm', cr)

    def _create_pickings_and_procurements(self, cr, uid, order, order_lines,
                                          picking_id=False, context=None):
        res = {}
        normal_lines = []
        dropship_lines = []
        dropship_flows = ('direct_delivery', 'direct_invoice_and_delivery')
        for line in order_lines:
            if (line.type == 'make_to_order' and
                    line.sale_flow in dropship_flows):
                dropship_lines.append(line)
            else:
                normal_lines.append(line)
        self._create_procurements_direct_mto(cr, uid, order, dropship_lines,
                                             context=context)
        res = super(sale_order, self)._create_pickings_and_procurements(
            cr, uid, order, normal_lines, picking_id, context)
        return res

    def action_button_confirm(self, cr, uid, ids, context=None):
        for sale in self.browse(cr, uid, ids, context=context):
            for line in sale.order_line:
                if (line.type == 'make_to_order' and
                    line.sale_flow in
                        ('direct_delivery', 'direct_invoice_and_delivery') and
                        not line.product_id.seller_ids):
                    raise orm.except_orm(_('Warning!'),
                                         _('Please set at least one supplier '
                                           'on the product: "%s" (code: %s)') %
                                          (line.product_id.name,
                                           line.product_id.default_code,))
        return super(sale_order, self).action_button_confirm(cr, uid, ids,
                                                             context=context)


class procurement_order(orm.Model):
    _inherit = 'procurement.order'

    _columns = {
        'sale_order_line_id': fields.many2one(
            'sale.order.line', 'Sale Order Line'),
    }

    def create_procurement_purchase_order(
        self, cr, uid, procurement, po_vals, line_vals,
        context=None
    ):
        if procurement.sale_order_line_id:
            warehouse_id = (
                procurement.sale_order_line_id.order_id.shop_id.warehouse_id)
            sale_flow = procurement.sale_order_line_id.sale_flow
            purchase_obj = self.pool.get('purchase.order')
            vals = purchase_obj.sale_flow_change(
                cr, uid, [], sale_flow,
                procurement.sale_order_line_id.order_id.id,
                warehouse_id.id, context=context)
            po_vals.update(vals.get('value', {}))

            po_vals.update({
                'sale_flow': sale_flow,
                'sale_id': procurement.sale_order_line_id.order_id.id})
            l_id = (
                procurement.sale_order_line_id.id
                if procurement.sale_order_line_id else False
                )
            line_vals.update({'sale_order_line_id': l_id})
        return super(
            procurement_order, self).create_procurement_purchase_order(
                cr, uid, procurement,
                po_vals, line_vals, context)

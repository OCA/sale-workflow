# -*- coding: utf-8 -*-

from osv import fields, osv
from tools.translate import _
from openerp import SUPERUSER_ID

"""
* Pre-book stock while sale order is not yet confirmed.
    Create a stock move (without picking and procurement) to decrease virtual stock. That reservation gets updated with the sale order line.
    If a reservation is existing at order confirmation, use it in the generated picking.
"""

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """ Delete prebookings """
        if context is None:
            context={}
        unlink_ids=[]
        for line in order_lines:
            for move in line.move_ids:
                #we don't expect this method to be called outside quotation confirmation
                assert move.state == 'waiting' and move.picking_id.id is False, _("Internal Error")
                unlink_ids.append(move.id)
        ctx=context.copy()
        ctx['call_unlink']=True #allow to delete non draft moves
        self.pool.get('stock.move').unlink(cr, uid, unlink_ids, context=ctx)

        return super(sale_order,self)._create_pickings_and_procurements(cr, uid, order, order_lines, picking_id=picking_id, context=context)

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def _prebook(self, cr, uid, ids, context=None):
        sale_obj=self.pool.get('sale.order')
        move_obj=self.pool.get('stock.move')
        for line in self.browse(cr,uid,ids,context=context):
            if line.move_ids: #there are already moves linked to the line, don't create new one
                continue
            order=line.order_id
            picking_id=False
            date_planned = sale_obj._get_date_planned(cr, uid, order, line, order.date_order, context=context)
            move=sale_obj._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=None)
                #module sale_stock
                #   location_id = order.shop_id.warehouse_id.lot_stock_id.id
                #   output_id = order.shop_id.warehouse_id.lot_output_id.id
                #   return {
                #       'name': line.name,
                #       'picking_id': picking_id,
                #       'product_id': line.product_id.id,
                #       'date': date_planned,
                #       'date_expected': date_planned,
                #       'product_qty': line.product_uom_qty,
                #       'product_uom': line.product_uom.id,
                #       'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
                #       'product_uos': (line.product_uos and line.product_uos.id)\
                #               or line.product_uom.id,
                #       'product_packaging': line.product_packaging.id,
                #       'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                #       'location_id': location_id,
                #       'location_dest_id': output_id,
                #       'sale_line_id': line.id,
                #       'tracking_id': False,
                #       'state': 'draft',
                #       #'state': 'waiting',
                #       'company_id': order.company_id.id,
                #       'price_unit': line.product_id.standard_price or 0.0
                #   }
            move['state']='waiting' #ensure move don't get processed
            move_id = move_obj.create(cr, uid, move, context=context)



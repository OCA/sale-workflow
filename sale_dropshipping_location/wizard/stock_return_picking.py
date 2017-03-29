# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              Jordi Ballester Alomar <jordi.ballester@eficent.com>
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

from openerp import netsvc
import time

from openerp.osv import osv,fields
from openerp.tools.translate import _


class stock_return_picking(osv.osv_memory):
    _inherit = 'stock.return.picking'


    def create_returns(self, cr, uid, ids, context=None):
        """
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.memory')
        act_obj = self.pool.get('ir.actions.act_window')
        model_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = True
        returned_lines = 0

#        Create new picking for returned products

        seq_obj_name = 'stock.picking'
        new_type = 'internal'
        if pick.type =='out':
            new_type = 'in'
            seq_obj_name = 'stock.picking.in'
        elif pick.type =='in':
            new_type = 'out'
            seq_obj_name = 'stock.picking.out'

        #The shipping address in the new stock picking is the supplier's
        partner_id = pick.partner_id.id
        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            move = move_obj.browse(cr, uid, mov_id, context=context)
            if move.purchase_line_id \
                and move.purchase_line_id.order_id \
                and move.purchase_line_id.order_id.sale_flow in \
                    ('direct_delivery', 'direct_invoice_and_delivery'):
                partner_id = move.purchase_line_id.order_id.partner_id.id
                continue

        new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        new_picking = pick_obj.copy(cr, uid, pick.id, {
                                        'name': _('%s-%s-return') % (new_pick_name, pick.name),
                                        'move_lines': [],
                                        'state':'draft',
                                        'type': new_type,
                                        'date':date_cur,
                                        'invoice_state': data['invoice_state'],
                                        'partner_id': partner_id,  # Added
        })

        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            if not mov_id:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)

            new_location = move.location_dest_id.id

            returned_qty = move.product_qty
            for rec in move.move_history_ids2:
                returned_qty -= rec.product_qty

            if returned_qty != new_qty:
                set_invoice_state_to_none = False
            if new_qty:
                returned_lines += 1
                # Introduce here the change - Change destination location
                # to be the one used for drop shipment returns.
                # Replace: move.location_id.id
                new_dest_location = move.location_id.id
                if move.purchase_line_id \
                    and move.purchase_line_id.order_id \
                    and move.purchase_line_id.order_id.sale_flow in \
                        ('direct_delivery', 'direct_invoice_and_delivery'):

                    warehouse = move.purchase_line_id.order_id.warehouse_id

                    if warehouse.property_stock_drop_ship_return:
                        new_dest_location = warehouse.property_stock_drop_ship_return.id
                    else:
                        raise osv.except_osv(
                            _('Error!'),
                            _('Must indicate a Drop Shipment return location.'))
                new_move=move_obj.copy(cr, uid, move.id, {
                                            'product_qty': new_qty,
                                            'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                                            'picking_id': new_picking,
                                            'state': 'draft',
                                            'location_id': new_location,
                                            'location_dest_id': new_dest_location,
                                            'date': date_cur,
                })
                move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4,new_move)]}, context=context)
        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        if set_invoice_state_to_none:
            pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'}, context=context)
        wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
        pick_obj.force_assign(cr, uid, [new_picking], context)
        # Update view id in context, lp:702939
        model_list = {
                'out': 'stock.picking.out',
                'in': 'stock.picking.in',
                'internal': 'stock.picking',
        }
        return {
            'domain': "[('id', 'in', ["+str(new_picking)+"])]",
            'name': _('Returned Picking'),
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model': model_list.get(new_type, 'stock.picking'),
            'type':'ir.actions.act_window',
            'context':context,
        }
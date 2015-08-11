# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Odoo.com.
#    Copyright (C) 2015 Openies.com.
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class SaleOrder(models.Model):
    
    _inherit = 'sale.order'
    
    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        vals = super(SaleOrder, self)._prepare_order_line_procurement(cr, uid, order, line, group_id, context)
        if line and line.address_allotment_id:
            vals['partner_dest_id'] = line.address_allotment_id.id
        return vals
    
class procurement_order(models.Model):
    
    _inherit = 'procurement.order'
    
    def _run_move_create(self, cr, uid, procurement, context=None):
        vals = super(procurement_order, self)._run_move_create(cr, uid, procurement, context)
        if procurement.partner_dest_id.id:
            vals.update({'partner_id': procurement.partner_dest_id.id})
        return vals
    
class StockMove(models.Model):
    
    _inherit = 'stock.move'
    
    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        partner_dict = {}
        vals = super(StockMove, self)._picking_assign(cr, uid, move_ids, procurement_group, location_from, location_to, context)
        move_rec = self.browse(cr, uid, move_ids, context=context)
        for move in move_rec:
            if not partner_dict.get(move.partner_id.id, False):
                partner_dict.update({move.partner_id.id : [move.id]})
            else:
                partner_dict.get(move.partner_id.id).append(move.id)
        pick_obj = self.pool.get('stock.picking')
        for key in partner_dict.keys():
            move = move_rec[0]
            if partner_dict.keys().index(key) == 0:
                self.write(cr, uid, partner_dict.get(key), {'partner_id': key}, context=context)
                pick_obj.write(cr, uid, [move.picking_id.id],{'partner_id': key}, context=context)
            else:
                values = {
                    'origin': move.origin,
                    'company_id': move.company_id and move.company_id.id or False,
                    'move_type': move.group_id and move.group_id.move_type or 'direct',
                    'partner_id': key or False,
                    'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
                }
                pick = pick_obj.create(cr, uid, values, context=context)
                self.write(cr, uid, partner_dict.get(key), {'picking_id': pick}, context=context)
        return vals
        


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

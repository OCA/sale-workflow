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

from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _picking_assign(self, procurement_group, location_from, location_to):
        '''Assign the moves to one picking per partner

        This method lets the upstream code create the first picking,
        and duplicates its header as required for each partner, dispatching
        the stock moves among all the pickings.

        @return: the value of the super() method.
        '''
        res = super(StockMove, self)._picking_assign(
            procurement_group, location_from, location_to)

        # We'll gather the pickings and moves per partner
        move_iter = iter(self)
        # The first move is obvious: we keep super's values
        first_move = next(move_iter)
        first_picking = first_move.picking_id
        first_picking.partner_id = first_move.partner_id
        picking_move_dict = {
            first_move.partner_id: [first_picking, first_move]
        }
        # Process the other moves
        for move in move_iter:
            if picking_move_dict.get(move.partner_id, False):
                # Known partner: enlist the stock move
                picking_move_dict[move.partner_id][1] += move
            else:
                # First time we get this partner: create the related picking
                new_picking = first_picking.copy(
                    {'partner_id': move.partner_id.id,
                     'move_lines': False})
                picking_move_dict[move.partner_id] = [new_picking, move]

        # Attach the moves to the right pickings (1 query per picking)
        for picking, moves in picking_move_dict.values():
            moves.write({'picking_id': picking.id})
            picking.action_confirm()
        return res

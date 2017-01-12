# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        if self.procurement_id.carrier_id:
            res['carrier_id'] = self.procurement_id.carrier_id.id
        res = super(StockMove, self)._get_new_picking_values()
        return res

    # Below comment is from Odoo sources
    # TDE DECORATOR: remove that api.multi when action_confirm is migrated
    @api.multi
    def assign_picking(self):

        Picking = self.env['stock.picking']
        self.recompute()

        for move in self:
            picking = Picking.search([
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft',
                                 'confirmed',
                                 'waiting',
                                 'partially_available',
                                 'assigned'])], limit=1)
            if not picking:
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
        return True
        # return super(StockMove, self).assign_picking()
        # ELSE return super
        #
# move.procurement_id.sale_line_id.order_id.carrier_id

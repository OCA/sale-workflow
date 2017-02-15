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
        return res

    @api.multi
    def assign_picking(self):
        res = super(StockMove, self).assign_picking()      
        # If moves come from a manual delivery from SO, we
        # Set the printed field to True in order to be sure no other moves
        # will go in this delivery.
        for move in self:
            if move.picking_id.sale_id.manual_delivery:
                if not move.picking_id.printed:
                    move.picking_id.write({'printed':True})
        return res

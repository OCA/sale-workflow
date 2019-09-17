# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def assign_picking(self):
        # Redefine method to filter on date_expected (allows to group moves
        # from the same manual delivery in one delivery)
        Picking = self.env['stock.picking']
        self.recompute()
        res = True
        for move in self:
            if not move.procurement_id.manual_delivery:
                res = super(StockMove, move).assign_picking()
                continue
            domain = [
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('min_date', '=', move.date_expected),
                ('max_date', '=', move.date_expected),
                ('state', 'in', ['draft', 'confirmed', 'waiting',
                                 'partially_available', 'assigned'])]
            picking = Picking.search(domain, limit=1)
            if not picking.sale_id.manual_delivery:
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
        return res

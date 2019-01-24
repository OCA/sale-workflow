# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    workflow_process_id = fields.Many2one(
        comodel_name="sale.workflow.process", string="Sale Workflow Process"
    )

    @api.multi
    def validate_picking(self):
        for picking in self:
            for move in picking.move_lines:
                total_move_qty = move.product_uom_qty
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
                    total_move_qty -= move_line.product_uom_qty
                if total_move_qty > 0:
                    move_line_vals = {
                        'product_uom_id': move.product_uom.id,
                        'picking_id': move.picking_id.id,
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'qty_done': total_move_qty,
                    }
                    self.env['stock.move.line'].create(move_line_vals)
            picking.button_validate()
        return True

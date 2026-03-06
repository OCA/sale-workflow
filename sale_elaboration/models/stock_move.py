# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = ["stock.move", "product.elaboration.mixin"]
    _name = "stock.move"

    # Helper fields to display elaborations in tree view
    sale_id = fields.Many2one(
        comodel_name="sale.order", compute="_compute_sale_related_data"
    )
    salesman_id = fields.Many2one(
        comodel_name="res.users", compute="_compute_sale_related_data"
    )
    order_date = fields.Datetime(compute="_compute_sale_related_data")
    sequence_code = fields.Char(compute="_compute_sale_related_data")

    def _compute_sale_related_data(self):
        # Get all chained moves to get sale line
        for move in self:
            moves = self.browse(list(self._rollup_move_dests({move.id})))
            move_sale = moves.filtered("sale_line_id")[:1]
            move.sale_id = move_sale.sale_line_id.order_id
            move.salesman_id = move_sale.sale_line_id.order_id.user_id
            move.order_date = move_sale.sale_line_id.date_order
            move.sequence_code = move.picking_type_id.sequence_code

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        """Don't merge moves with distinct elaborations"""
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields += ["elaboration_ids", "elaboration_note"]
        return distinct_fields

    def write(self, vals):
        # Propagate elaboration quantities to sale order line when quantity_done changes
        # in done moves (unlock picking)
        res = False
        if "quantity" in vals and self[:1].state == "done":
            moves_with_elaborations = self.filtered(
                lambda m: m.sale_line_id and m.elaboration_ids
            )
            old_quantities = {move: move.quantity for move in moves_with_elaborations}
            res = super().write(vals)
            for move in moves_with_elaborations:
                qty_difference = move.quantity - old_quantities[move]
                if not qty_difference:
                    continue
                for move_elab in move.elaboration_ids:
                    sale_elab = move.sale_line_id.order_id.order_line.filtered(
                        lambda x, move_elab=move_elab: x.product_id
                        == move_elab.product_id
                    )[:1]
                    if sale_elab:
                        sale_elab.product_uom_qty += qty_difference
        return res or super().write(vals)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    elaboration_ids = fields.Many2many(related="move_id.elaboration_ids")
    elaboration_note = fields.Char(related="move_id.elaboration_note")

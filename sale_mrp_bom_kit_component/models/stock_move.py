# Copyright 2026 Eshan Desle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _compute_kit_quantities(self, product_id, kit_qty, kit_bom, filters):
        """
        Override to compute delivered quantities accurately for customized kits.
        Only considers components that were selected on the sale order line,
        using their customized quantities.
        """
        sale_lines = self.mapped("sale_line_id").filtered(
            lambda line: line.is_kit and line.kit_component_ids
        )
        if not sale_lines:
            return super()._compute_kit_quantities(
                product_id, kit_qty, kit_bom, filters
            )

        sale_line = sale_lines[0]
        selected_comps = sale_line.kit_component_ids.filtered("is_selected")
        if not selected_comps:
            return kit_qty

        qty_ratios = []
        kit_qty = kit_qty / (kit_bom.product_qty or 1.0)

        def get_qty(move):
            if move.picked:
                return move.product_uom._compute_quantity(
                    move.quantity, move.product_id.uom_id, rounding_method="HALF-UP"
                )
            return move.product_qty

        for comp in selected_comps:
            if comp.product_id.type == "service":
                continue
            if comp.product_uom_id.is_zero(comp.product_qty):
                continue
            bom_line_moves = self.filtered(
                lambda m, c=comp: (c.bom_line_id and m.bom_line_id == c.bom_line_id)
                or m.product_id == c.product_id
            )
            if not bom_line_moves:
                return 0.0

            uom_qty_per_kit = comp.product_qty
            qty_per_kit = comp.product_uom_id._compute_quantity(
                uom_qty_per_kit / (kit_bom.product_qty or 1.0),
                comp.product_id.uom_id,
                round=False,
            )
            if not qty_per_kit:
                continue

            incoming_moves = bom_line_moves.filtered(filters["incoming_moves"])
            final_incoming_moves = incoming_moves - incoming_moves.move_orig_ids
            incoming_qty = sum(final_incoming_moves.mapped(get_qty))
            outgoing_moves = bom_line_moves.filtered(filters["outgoing_moves"])
            final_outgoing_moves = outgoing_moves - outgoing_moves.move_orig_ids
            outgoing_qty = sum(final_outgoing_moves.mapped(get_qty))
            qty_processed = incoming_qty - outgoing_qty

            qty_ratios.append(comp.product_id.uom_id.round(qty_processed / qty_per_kit))

        if qty_ratios:
            return int(min(qty_ratios))
        return 0.0

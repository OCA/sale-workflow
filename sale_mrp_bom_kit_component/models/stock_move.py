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
        matching_sale_lines = self.mapped("sale_line_id").filtered(
            lambda line: line.product_id == product_id
            and line.is_kit
            and line.kit_component_ids
        )
        if not matching_sale_lines:
            return super()._compute_kit_quantities(
                product_id, kit_qty, kit_bom, filters
            )

        if len(matching_sale_lines) > 1:
            total_delivered = 0.0
            for sale_line in matching_sale_lines:
                line_moves = self.filtered(lambda m, sl=sale_line: m.sale_line_id == sl)
                line_kit_bom = sale_line._get_kit_bom() or kit_bom
                order_qty = sale_line.product_uom_id._compute_quantity(
                    sale_line.product_uom_qty, line_kit_bom.product_uom_id
                )
                total_delivered += line_moves._compute_kit_quantities(
                    product_id, order_qty, line_kit_bom, filters
                )
            return total_delivered

        sale_line = matching_sale_lines[0]
        selected_comps = sale_line.kit_component_ids.filtered("is_selected")
        if not selected_comps:
            return 0.0

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
            if comp.bom_line_id:
                bom_line_moves = self.filtered(
                    lambda m, c=comp: m.bom_line_id == c.bom_line_id
                )
            else:
                bom_line_moves = self.filtered(
                    lambda m, c=comp: m.product_id == c.product_id and not m.bom_line_id
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
            return min(qty_ratios) // 1
        return 0.0

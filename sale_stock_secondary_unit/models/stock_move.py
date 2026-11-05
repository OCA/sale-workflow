# Copyright 2026 Tecnativa - Carlos Dauden

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        # A multi-step "buy" route procures an intermediate move (e.g. the
        # vendor receipt), which has no sale_line_id of its own - only the
        # eventual delivery move, elsewhere in its chain, is linked to the
        # sale order line. sale_stock's own _get_sale_order_lines() already
        # walks the whole chain (both directions) to find it.
        sale_line = self.sale_line_id or self._get_sale_order_lines()[:1]
        vals["secondary_uom_id"] = sale_line.secondary_uom_id.id
        vals["secondary_uom_qty"] = self.env.context.get(
            "procure_secondary_uom_qty", {}
        ).get(self.id, sale_line.secondary_uom_qty)
        return vals

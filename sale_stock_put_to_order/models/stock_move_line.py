# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _apply_putaway_strategy(self):
        auto_select = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_stock_put_to_order.auto_select_location")
            == "True"
        )
        if not auto_select:
            return super()._apply_putaway_strategy()

        pto_handled = self.browse()
        resolved_cache = {}
        for sml in self:
            picking = sml.picking_id
            if not picking:
                continue
            if picking.id not in resolved_cache:
                root = picking._get_pto_root_location()
                if root:
                    dest = next(
                        (
                            loc
                            for loc, _ in (picking._find_pto_dest_location_and_quants())
                        ),
                        None,
                    )
                else:
                    dest = None
                resolved_cache[picking.id] = dest
            dest = resolved_cache[picking.id]
            if dest:
                sml.location_dest_id = dest
                pto_handled |= sml

        remaining = self - pto_handled
        if remaining:
            super(StockMoveLine, remaining)._apply_putaway_strategy()

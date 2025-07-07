# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def action_view_stock_moves(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Stock Moves History for %s") % self.product_id.display_name,
            "res_model": "stock.move.line",
            "view_mode": "list",
            "views": [
                (
                    self.env.ref(
                        "sale_order_line_stock_move_history.stock_move_line_history"
                    ).id,
                    "list",
                ),
            ],
            "domain": [
                ("move_id.sale_line_id", "=", self.id),
                ("product_id", "=", self.product_id.id),
            ],
            "context": {
                "default_product_id": self.product_id.id,
            },
        }

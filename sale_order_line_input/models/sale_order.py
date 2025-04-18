# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sol_count = fields.Integer(compute="_compute_sol_count")

    def _compute_sol_count(self):
        for rec in self:
            rec.sol_count = len(rec.order_line)

    def action_view_sale_order_line(self):
        self.ensure_one()
        return {
            "name": _("SO Lines"),
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "sale.order.line",
            "domain": [("order_id", "=", self.id)],
            "context": {"default_order_id": self.id},
            "views": [
                [
                    self.env.ref(
                        "sale_order_line_input.view_sales_order_line_input_tree_inherit"
                    ).id,
                    "tree",
                ]
            ],
        }

# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from ast import literal_eval

from odoo import fields, models
from odoo.fields import Domain


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_line_count = fields.Integer(compute="_compute_order_line_count")

    def _compute_order_line_count(self):
        for order in self:
            order.order_line_count = len(
                order.order_line.filtered(lambda line: not line.display_type)
            )

    def action_view_order_lines(self):
        """Open the sale order lines of this order in a dedicated list.

        Reuses the standard sale order line list/form views so users can
        search/filter lines and edit prices, quantities, uom, etc. subject
        to the same restrictions as the sale order form (see
        ``sale.order.line`` readonly fields and its ``write`` override).
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale_order_line_smartbutton.sale_order_line_action"
        )
        action["domain"] = Domain(literal_eval(action.get("domain") or "[]")) & Domain(
            "order_id", "=", self.id
        )
        action["context"] = {"default_order_id": self.id}
        return action

# Copyright 2025 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "order_line.product_id.service_policy", "order_line.product_id.service_tracking"
    )
    def _compute_is_product_milestone(self):
        """Override to show milestone button also for milestone_project tracking"""
        for order in self:
            order.is_product_milestone = order.order_line.product_id.filtered(
                lambda p: p.service_policy == "delivered_milestones"
                or p.service_tracking == "milestone_project"
            )

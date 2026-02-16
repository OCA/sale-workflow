# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_forecast_available = fields.Boolean(
        string="Forecast Available",
        compute="_compute_sale_forecast_available",
        store=True,
        help="True if this line has forecast availability issues",
    )

    @api.depends("order_line.forecasted_issue")
    def _compute_sale_forecast_available(self):
        for order in self:
            order.sale_forecast_available = not any(
                line.forecasted_issue
                for line in order.order_line
                if not line.display_type
            )

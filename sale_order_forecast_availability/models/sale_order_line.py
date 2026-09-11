# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    forecasted_issue = fields.Boolean(
        compute="_compute_forecasted_issue",
        store=True,
        help="True if this line has forecast availability issues",
    )

    @api.depends(
        "scheduled_date",
        "free_qty_today",
        "virtual_available_at_date",
        "qty_to_deliver",
        "forecast_expected_date",
        "is_mto",
        "state",
    )
    def _compute_forecasted_issue(self):
        for line in self:
            forecasted_issue = False
            if not line.scheduled_date or line.display_type:
                line.forecasted_issue = False
                continue
            if line.state == "sale":
                will_be_fulfilled = line.free_qty_today >= line.qty_to_deliver
            else:
                will_be_fulfilled = (
                    line.virtual_available_at_date >= line.qty_to_deliver
                )
            will_be_late = (
                line.forecast_expected_date
                and line.forecast_expected_date > line.scheduled_date
            )
            if line.state in ["draft", "sent"]:
                forecasted_issue = not will_be_fulfilled and not line.is_mto
            else:
                forecasted_issue = not will_be_fulfilled or will_be_late
            line.forecasted_issue = forecasted_issue

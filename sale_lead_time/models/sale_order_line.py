# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id", "order_id.delivery_lead_time")
    def _compute_customer_lead(self):
        super()._compute_customer_lead()
        for line in self:
            line.customer_lead += line.order_id.delivery_lead_time
        return

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        if values.get("date_planned"):
            values["date_planned"] -= timedelta(days=self.order_id.delivery_lead_time)
        return values

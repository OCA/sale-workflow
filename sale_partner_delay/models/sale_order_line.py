# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.partner_id")
    def _compute_customer_lead(self):  # pylint: disable=missing-return
        # OVERRIDE to add the partner delay to the customer lead
        # This method must run after the one in `sale_stock`, to effectively
        # add the partner delay to the product delay.
        super()._compute_customer_lead()
        for line in self:
            line.customer_lead += line.order_id.partner_id.sale_delay

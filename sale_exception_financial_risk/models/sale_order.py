# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    risk_amount = fields.Monetary(
        string="Risk amount",
        compute="_compute_risk_amount",
        compute_sudo=True,
        store=True,
    )

    @api.depends("state", "currency_id", "amount_total", "company_id", "date_order")
    def _compute_risk_amount(self):
        for item in self:
            item.risk_amount = item.currency_id._convert(
                item.amount_total,
                item.company_id.currency_id,
                item.company_id,
                item.date_order
                and item.date_order.date()
                or fields.Date.context_today(item),
                round=False,
            )

    def action_confirm(self):
        if not self.env.context.get("bypass_risk", False):
            self._check_exception()
        return super().action_confirm()

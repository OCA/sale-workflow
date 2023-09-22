# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    percentage = fields.Integer("Winning sale %", default=50)
    expected_amount_cur = fields.Monetary(
        "Expected Amount in currency",
        compute="_compute_expected_amount_cur",
        currency_field="company_currency_id",
        store=True,
    )

    def action_confirm(self):
        res = super().action_confirm()
        if res:
            self.percentage = 100
        else:
            return res

    def action_cancel(self):
        res = super().action_cancel()
        if res:
            self.percentage = 0
        else:
            return res

    @api.depends("amount_total_curr", "percentage")
    def _compute_expected_amount_cur(self):
        for record in self:
            record.expected_amount_cur = (
                record.amount_total_curr * record.percentage / 100
            )

# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleCouponProgram(models.Model):
    """Extend to add logic that control multi coupon usage."""

    _inherit = "sale.coupon.program"

    # Changing existing related field to computed to allow changing
    # currency.
    currency_id = fields.Many2one(
        "res.currency",
        related=None,
        compute="_compute_currency_id",
        inverse="_inverse_currency_id",
    )
    currency_custom_id = fields.Many2one("res.currency", "Custom Currency")

    @api.depends("company_id.currency_id", "currency_custom_id")
    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = rec.currency_custom_id or rec.company_id.currency_id

    def _inverse_currency_id(self):
        for rec in self:
            rec.currency_custom_id = rec.currency_id

# Copyright Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
        store=True,
    )
    amount_total_curr = fields.Monetary(
        string="Total Amount",
        readonly=True,
        help="Sale Order Amount in the company Currency",
        compute="_compute_amount_company",
        currency_field="company_currency_id",
        store=True,
    )

    @api.depends("amount_total", "currency_rate")
    def _compute_amount_company(self):
        for rec in self:
            to_amount = (
                rec.amount_total / rec.currency_rate if rec.currency_rate else 0.0
            )
            rec.amount_total_curr = to_amount

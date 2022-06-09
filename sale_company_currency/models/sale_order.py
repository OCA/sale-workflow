# Copyright Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
    )
    amount_total_curr = fields.Monetary(
        string="Total Amount",
        readonly=True,
        help="Sale Order Amount in the company Currency",
        compute="_compute_amount_company",
        currency_id="company_currency_id",
    )

    @api.multi
    @api.depends("amount_total")
    def _compute_amount_company(self):
        for so in self:
            if so.state in ("sale", "done"):
                so_date = so.confirmation_date
            else:
                so_date = so.date_order
            so.amount_total_curr = so.currency_id.with_context(date=so_date).compute(
                so.amount_total, so.company_id.currency_id
            )

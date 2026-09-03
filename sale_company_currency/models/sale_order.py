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
        for order in self:
            if order.currency_id.id == order.company_id.currency_id.id:
                to_amount = order.amount_total
            else:
                to_amount = order.amount_total * order.currency_rate
            order.amount_total_curr = to_amount

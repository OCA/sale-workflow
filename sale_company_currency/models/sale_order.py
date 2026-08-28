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

    @api.depends("amount_total", "currency_id", "company_id", "date_order")
    def _compute_amount_company(self):
        for order in self:
            # order.currency_id == order.company_id.currency_id: 
            if order.currency_id == order.company_id.currency_id:
                order.amount_total_curr = order.amount_total
            else:
                # Convert order amount to company currency
                conversion_date = (
                    order.date_order and order.date_order.date()
                    or fields.Date.context_today(self)
                )
                order.amount_total_curr = order.currency_id._convert(
                    order.amount_total,
                    order.company_id.currency_id,
                    order.company_id,
                    conversion_date,
                )

# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    currency_rate = fields.Float(
        compute="_compute_currency_rate",
        digits="Currency Rate Precision",
    )

    inverse_currency_rate = fields.Float(
        compute="_compute_currency_rate",
        digits="Currency Rate Precision",
    )

    sale_show_currency_rate = fields.Selection(
        string="Show Currency Rate",
        related="company_id.sale_show_currency_rate",
    )

    @api.depends("currency_id", "company_id.currency_id")
    def _compute_currency_rate(self):
        for order in self:
            if order.currency_id != order.company_id.currency_id:
                order.currency_rate = order.currency_id._convert(
                    1.0,
                    order.company_id.currency_id,
                    order.company_id,
                    order.date_order,
                    round=False,
                )
                order.inverse_currency_rate = order.company_id.currency_id._convert(
                    1.0,
                    order.currency_id,
                    order.company_id,
                    order.date_order,
                    round=False,
                )
            else:
                order.currency_rate = 1.0
                order.inverse_currency_rate = 1.0

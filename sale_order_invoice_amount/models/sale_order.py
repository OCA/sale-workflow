# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from odoo import api, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "order_line.tax_id",
        "order_line.price_unit",
        "amount_total",
        "amount_untaxed",
        "state",
        "invoice_ids",
        "invoice_ids.amount_total_in_currency_signed",
        "amount_total",
        "invoice_ids.state",
    )
    def _compute_tax_totals(self):
        res = super()._compute_tax_totals()
        for order in self:
            lang_env = order.with_context(lang=order.partner_id.lang).env
            order.tax_totals.update(
                {
                    "amount_invoiced": order.amount_invoiced,
                    "formatted_amount_invoiced": formatLang(
                        lang_env, order.amount_invoiced, currency_obj=order.currency_id
                    ),
                    "amount_to_invoice": order.amount_to_invoice,
                    "formatted_amount_to_invoice": formatLang(
                        lang_env,
                        order.amount_to_invoice,
                        currency_obj=order.currency_id,
                    ),
                }
            )
        return res

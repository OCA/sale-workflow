# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from odoo import api, fields, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoiced_amount = fields.Monetary(
        compute="_compute_invoice_amount",
        store=True,
        help="Order amount already invoiced.",
    )

    uninvoiced_amount = fields.Monetary(
        compute="_compute_invoice_amount",
        store=True,
        help="Order amount to be invoiced",
    )

    @api.depends(
        "state",
        "invoice_ids",
        "invoice_ids.amount_total_in_currency_signed",
        "amount_total",
        "invoice_ids.state",
    )
    def _compute_invoice_amount(self):
        for rec in self:
            if rec.state != "cancel" and rec.invoice_ids:
                invoiced_amount = 0.0
                for invoice in rec.invoice_ids:
                    if invoice.state != "cancel":
                        invoiced_amount += invoice.amount_total_in_currency_signed
                rec.invoiced_amount = invoiced_amount
                rec.uninvoiced_amount = max(0, rec.amount_total - rec.invoiced_amount)
            else:
                rec.invoiced_amount = 0.0
                if rec.state in ["draft", "sent", "cancel"]:
                    rec.uninvoiced_amount = 0.0
                else:
                    rec.uninvoiced_amount = rec.amount_total

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
                    "invoiced_amount": order.invoiced_amount,
                    "formatted_invoiced_amount": formatLang(
                        lang_env, order.invoiced_amount, currency_obj=order.currency_id
                    ),
                    "uninvoiced_amount": order.uninvoiced_amount,
                    "formatted_uninvoiced_amount": formatLang(
                        lang_env,
                        order.uninvoiced_amount,
                        currency_obj=order.currency_id,
                    ),
                }
            )
        return res

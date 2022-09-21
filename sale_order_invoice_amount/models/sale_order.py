# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
import json

from odoo import api, fields, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoiced_amount = fields.Monetary(
        compute="_compute_invoice_amount",
        store=True,
    )

    uninvoiced_amount = fields.Monetary(
        compute="_compute_invoice_amount",
        store=True,
    )

    @api.depends(
        "state",
        "invoice_ids",
        "invoice_ids.amount_total_signed",
        "amount_total",
        "invoice_ids.state",
    )
    def _compute_invoice_amount(self):
        for rec in self:
            if rec.state != "cancel" and rec.invoice_ids:
                rec.invoiced_amount = 0.0
                for invoice in rec.invoice_ids:
                    if invoice.state != "cancel":
                        rec.invoiced_amount += invoice.amount_total_signed
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
        "invoice_ids.amount_total_signed",
        "amount_total",
        "invoice_ids.state",
    )
    def _compute_tax_totals_json(self):
        res = super(SaleOrder, self)._compute_tax_totals_json()
        lang_env = self.with_context(lang=self.partner_id.lang).env
        total_json = json.loads(self.tax_totals_json)
        total_json.update(
            {
                "invoiced_amount": self.invoiced_amount,
                "formatted_invoiced_amount": formatLang(
                    lang_env, self.invoiced_amount, currency_obj=self.currency_id
                ),
                "uninvoiced_amount": self.uninvoiced_amount,
                "formatted_uninvoiced_amount": formatLang(
                    lang_env, self.uninvoiced_amount, currency_obj=self.currency_id
                ),
            }
        )
        self.tax_totals_json = json.dumps(total_json)
        return res

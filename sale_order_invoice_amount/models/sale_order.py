# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from odoo import api, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "state",
        "invoice_ids",
        "invoice_ids.amount_total_in_currency_signed",
        "amount_total",
        "invoice_ids.state",
    )
    def _compute_amount_invoiced(self):
        if not self.env.company.enable_amount_invoiced_based_on_quantity:
            return super()._compute_amount_invoiced()
        else:
            zero_records = self.browse()
            for rec in self:
                if rec.state != "cancel" and rec.invoice_ids:
                    total = 0.0
                    for invoice in rec.invoice_ids:
                        if invoice.state != "cancel":
                            if (
                                invoice.currency_id != rec.currency_id
                                and rec.currency_id != invoice.company_currency_id
                            ):
                                invoices = rec.invoice_ids.filtered(
                                    lambda x: x.state == "posted"
                                )
                                total += invoices._get_sale_order_invoiced_amount(rec)
                            else:
                                total += invoice.amount_total_signed
                    rec.amount_invoiced = total
                else:
                    zero_records |= rec
            if zero_records:
                zero_records.amount_invoiced = 0.0

    # Amount to invoice could not be equal to total - amount invoiced.
    # For example if the amount invoiced does not match with the price unit.
    @api.depends("invoice_ids.state")
    def _compute_amount_to_invoice(self):
        if not self.env.company.enable_amount_invoiced_based_on_quantity:
            return super()._compute_amount_to_invoice()
        else:
            zero_records = self.browse()
            for rec in self:
                if rec.state in ["draft", "sent", "cancel"]:
                    zero_records |= rec
                else:
                    rec.amount_to_invoice = max(
                        0,
                        sum(
                            (line.product_uom_qty - line.qty_invoiced)
                            * (line.price_total / line.product_uom_qty)
                            for line in rec.order_line.filtered(
                                lambda sl: sl.product_uom_qty > 0
                            )
                        ),
                    )
            if zero_records:
                zero_records.amount_to_invoice = 0.0

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

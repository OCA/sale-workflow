# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "qty_invoiced",
        "qty_delivered",
        "product_uom_qty",
        "state",
        "order_id.invoice_policy",
    )
    def _compute_qty_to_invoice(self):
        other_lines = self.filtered(
            lambda l: l.product_id.type == "service"
            or not l.order_id.invoice_policy
            or not l.order_id.invoice_policy_required
        )
        super(SaleOrderLine, other_lines)._compute_qty_to_invoice()
        for line in self - other_lines:
            invoice_policy = line.order_id.invoice_policy
            if invoice_policy == "order":
                line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
            else:
                line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
        return True

    @api.depends(
        "state",
        "price_reduce",
        "product_id",
        "untaxed_amount_invoiced",
        "qty_delivered",
        "product_uom_qty",
        "order_id.invoice_policy",
    )
    def _compute_untaxed_amount_to_invoice(self):
        other_lines = self.filtered(
            lambda line: line.product_id.type == "service"
            or not line.order_id.invoice_policy
            or line.order_id.invoice_policy == line.product_id.invoice_policy
            or line.state not in ["sale", "done"]
            or not line.order_id.invoice_policy_required
        )
        super(SaleOrderLine, other_lines)._compute_untaxed_amount_to_invoice()
        for line in self - other_lines:
            invoice_policy = line.order_id.invoice_policy
            amount_to_invoice = 0.0
            price_subtotal = 0.0
            uom_qty_to_consider = (
                line.qty_delivered
                if invoice_policy == "delivery"
                else line.product_uom_qty
            )
            price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_subtotal = price_reduce * uom_qty_to_consider
            if len(line.tax_id.filtered(lambda tax: tax.price_include)) > 0:
                price_subtotal = line.tax_id.compute_all(
                    price_reduce,
                    currency=line.currency_id,
                    quantity=uom_qty_to_consider,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )["total_excluded"]
            inv_lines = line._get_invoice_lines()
            if any(inv_lines.mapped(lambda l: l.discount != line.discount)):
                amount = 0
                for inv_line in inv_lines:
                    if (
                        len(inv_line.tax_ids.filtered(lambda tax: tax.price_include))
                        > 0
                    ):
                        amount += inv_line.tax_ids.compute_all(
                            inv_line.currency_id._convert(
                                inv_line.price_unit,
                                line.currency_id,
                                line.company_id,
                                inv_line.date or fields.Date.today(),
                                round=False,
                            )
                            * inv_line.quantity
                        )["total_excluded"]
                    else:
                        amount += (
                            inv_line.currency_id._convert(
                                inv_line.price_unit,
                                line.currency_id,
                                line.company_id,
                                inv_line.date or fields.Date.today(),
                                round=False,
                            )
                            * inv_line.quantity
                        )
                amount_to_invoice = max(price_subtotal - amount, 0)
            else:
                amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced
            line.untaxed_amount_to_invoice = amount_to_invoice
        return True

# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    force_invoiced_quantity = fields.Float(
        digits="Product Unit of Measure",
        help=(
            "This amount will be deducted from quantity to invoice."
            "\nquantity to invoice = delivered - invoiced - force invoiced"
        ),
    )

    @api.depends("force_invoiced_quantity")
    def _compute_qty_to_invoice(self):
        """
        Compute the quantity to invoice.
        """
        res = super()._compute_qty_to_invoice()
        for line in self:
            if line.state in ["sale", "done"] and not line.display_type:
                if line.product_id.invoice_policy == "order":
                    line.qty_to_invoice = (
                        line.product_uom_qty
                        - line.qty_invoiced
                        - line.force_invoiced_quantity
                    )
                else:
                    line.qty_to_invoice = (
                        line.qty_delivered
                        - line.qty_invoiced
                        - line.force_invoiced_quantity
                    )
        return res

    @api.depends("force_invoiced_quantity")
    def _compute_untaxed_amount_to_invoice(self):
        """Total of remaining amount to invoice on the sale order line (taxes excl.) as
            total_sol - amount already invoiced
        where Total_sol depends on the invoice policy of the product.

        Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
        come only from the SO lines.
        """
        res = super()._compute_untaxed_amount_to_invoice()
        for line in self:
            amount_to_invoice = 0.0
            if line.state in ["sale", "done"]:
                price_subtotal = 0.0
                uom_qty_to_consider = (
                    line.qty_delivered
                    if line.product_id.invoice_policy == "delivery"
                    else line.product_uom_qty
                )
                uom_qty_to_consider -= line.force_invoiced_quantity
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
                if any(
                    inv_lines.mapped(
                        lambda inv_line: inv_line.discount != line.discount
                    )
                ):
                    amount = 0
                    for inv_line in inv_lines:
                        if (
                            len(
                                inv_line.tax_ids.filtered(lambda tax: tax.price_include)
                            )
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
        return res

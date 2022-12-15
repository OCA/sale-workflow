# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    origin_price_unit = fields.Float(digits="Product Price")

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if self._do_split_discount():
            res["discount_split_by_sale_line_id"] = self.id
        return res

    def _do_split_discount(self):
        self.ensure_one()
        return (
            self.company_id.account_split_discount_line
            and self.currency_id.compare_amounts(
                self.origin_price_unit, self.price_unit
            )
            == 1
        )

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "untaxed_amount_to_invoice",
    )
    def _compute_qty_invoiced(self):
        # OVERRIDE: take into account the new line for discount in the invoice.
        # Since the two lines (price and discount) are linked to the same sale
        # line, we avoid taking into account the discount line (or we would
        # have doubled the invoiced qty).
        res = super(SaleOrderLine, self)._compute_qty_invoiced()
        for line in self:
            if line.origin_price_unit:
                qty_invoiced = 0.0
                for invoice_line in line._get_invoice_lines():
                    if (
                        invoice_line.move_id.state != "cancel"
                        or invoice_line.move_id.payment_state == "invoicing_legacy"
                    ):
                        if (
                            invoice_line.move_id.move_type == "out_invoice"
                            and not invoice_line.is_split_discount_line
                        ):
                            qty_invoiced += (
                                invoice_line.product_uom_id._compute_quantity(
                                    invoice_line.quantity, line.product_uom
                                )
                            )
                        elif (
                            invoice_line.move_id.move_type == "out_refund"
                            and not invoice_line.is_split_discount_line
                        ):
                            qty_invoiced -= (
                                invoice_line.product_uom_id._compute_quantity(
                                    invoice_line.quantity, line.product_uom
                                )
                            )
                line.qty_invoiced = qty_invoiced
        return res

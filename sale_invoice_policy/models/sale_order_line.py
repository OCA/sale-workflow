# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from contextlib import contextmanager

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @contextmanager
    def _sale_invoice_policy(self, lines):
        """Apply the sale invoice policy to the products

        This method must be called with lines sharing the same invoice policy
        """
        invoice_policy = set(lines.mapped("order_id.invoice_policy"))
        if len(invoice_policy) > 1:
            raise Exception(
                "The method _sale_invoice_policy() must be called with lines "
                "sharing the same invoice policy"
            )
        invoice_policy = next(iter(invoice_policy))
        invoice_policy_field = self.env["product.product"]._fields["invoice_policy"]
        products = lines.product_id
        with self.env.protecting([invoice_policy_field], products):
            old_values = {}
            for product in products:
                old_values[product] = product.invoice_policy
                product.invoice_policy = invoice_policy
            yield
            for product, invoice_policy in old_values.items():
                product.invoice_policy = invoice_policy

    @api.depends("order_id.invoice_policy")
    def _compute_qty_to_invoice(self):
        """
        Exclude lines that have their order invoice policy filled in
        """
        other_lines = self.filtered(
            lambda line: line.product_id.type == "service"
            or line.order_id.invoice_policy == "product"
        )
        super(SaleOrderLine, other_lines)._compute_qty_to_invoice()
        for line in self - other_lines:
            invoice_policy = line.order_id.invoice_policy
            if invoice_policy == "order":
                line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
            else:
                line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
        return True

    @api.depends("order_id.invoice_policy")
    def _compute_untaxed_amount_to_invoice(self) -> None:
        other_lines = self.filtered(
            lambda line: line.product_id.type == "service"
            or line.order_id.invoice_policy == "product"
            or line.order_id.invoice_policy == line.product_id.invoice_policy
            or line.state not in ["sale", "done"]
        )
        super(SaleOrderLine, other_lines)._compute_untaxed_amount_to_invoice()
        for lines in (self - other_lines).partition("order_id.invoice_policy").values():
            with self._sale_invoice_policy(lines):
                super(SaleOrderLine, lines)._compute_untaxed_amount_to_invoice()
        return

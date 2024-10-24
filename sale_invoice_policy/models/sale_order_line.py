# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.invoice_policy")
    def _compute_qty_to_invoice(self):
        """
        Exclude lines that have their order invoice policy filled in
        """
        other_lines = self.filtered(
            lambda l: l.product_id.type == "service" or not l.order_id.invoice_policy
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
    def _compute_untaxed_amount_to_invoice(self):
        other_lines = self.filtered(
            lambda line: line.product_id.type == "service"
            or not line.order_id.invoice_policy
            or line.order_id.invoice_policy == line.product_id.invoice_policy
            or line.state not in ["sale", "done"]
        )
        super(SaleOrderLine, other_lines)._compute_untaxed_amount_to_invoice()
        for line in self - other_lines:
            # Save product invoice policy, change it to sale order one, add context manager
            # to not trigger other computes. Then, restablish former one.
            with self.env.norecompute():
                policy = line.product_id.invoice_policy
                line.product_id.invoice_policy = line.order_id.invoice_policy
            super(SaleOrderLine, line)._compute_untaxed_amount_to_invoice()
            with self.env.norecompute():
                line.product_id.invoice_policy = policy
        return

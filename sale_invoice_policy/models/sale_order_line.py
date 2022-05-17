# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.depends(
        "qty_invoiced",
        "qty_delivered",
        "product_uom_qty",
        "order_id.state",
        "order_id.invoice_policy",
    )
    def _get_to_invoice_qty(self):
        invoice_policies = set(self.mapped("order_id.invoice_policy"))
        line_by_id = {line.id: line for line in self}
        done_lines = self.env["sale.order.line"].browse()
        for invoice_policy in invoice_policies:
            so_lines = (
                self.with_context(invoice_policy=invoice_policy)
                .filtered(lambda x, p=invoice_policy: x.order_id.invoice_policy == p)
                .with_prefetch()
            )
            done_lines |= so_lines
            so_lines.mapped("product_id")
            if so_lines:
                super(SaleOrderLine, so_lines)._get_to_invoice_qty()
                for line in so_lines:
                    # due to the change of context in compute methods,
                    # assign the value in the modified context to self
                    line_by_id[line.id].qty_to_invoice = line.qty_to_invoice
        # Not to break function if (it could not happen) some records
        # were not in so_lines
        super(SaleOrderLine, self - done_lines)._get_to_invoice_qty()
        return True

    @api.depends(
        "state",
        "product_uom_qty",
        "qty_delivered",
        "qty_to_invoice",
        "qty_invoiced",
        "order_id.invoice_policy",
    )
    def _compute_invoice_status(self):
        invoice_policies = set(self.mapped("order_id.invoice_policy"))
        line_by_id = {line.id: line for line in self}
        done_lines = self.env["sale.order.line"].browse()
        for invoice_policy in invoice_policies:
            so_lines = (
                self.with_context(invoice_policy=invoice_policy)
                .filtered(lambda x, p=invoice_policy: x.order_id.invoice_policy == p)
                .with_prefetch()
            )
            done_lines |= so_lines
            if so_lines:
                super(SaleOrderLine, so_lines)._compute_invoice_status()
                for line in so_lines:
                    # due to the change of context in compute methods,
                    # assign the value in the modified context to self
                    line_by_id[line.id].invoice_status = line.invoice_status
        # Not to break function if (it could not happen) some records
        # were not in so_lines
        super(SaleOrderLine, self - done_lines)._compute_invoice_status()
        return True

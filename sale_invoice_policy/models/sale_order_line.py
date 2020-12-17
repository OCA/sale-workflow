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
        for line in self:
            ctx_line = line.with_context(invoice_policy=line.order_id.invoice_policy)
            super(SaleOrderLine, ctx_line)._get_to_invoice_qty()
            line.qty_to_invoice = ctx_line.qty_to_invoice

    @api.depends(
        "state",
        "product_uom_qty",
        "qty_delivered",
        "qty_to_invoice",
        "qty_invoiced",
        "order_id.invoice_policy",
    )
    def _compute_invoice_status(self):
        for line in self:
            ctx_line = line.with_context(invoice_policy=line.order_id.invoice_policy)
            super(SaleOrderLine, ctx_line)._compute_invoice_status()
            line.invoice_status = ctx_line.invoice_status

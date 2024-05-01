# Copyright <2022> <Janik von Rotz - Mint System>
# Copyright <2024> <Denis Leemann - Camptocamp SA>
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("qty_invoiced", "qty_delivered", "product_uom_qty", "order_id.state")
    def _get_to_invoice_qty(self):
        res = super()._get_to_invoice_qty()
        for line in self:
            if not line.product_id.billable:
                line.qty_to_invoice = 0
        return res

    @api.depends(
        "invoice_lines.move_id.state", "invoice_lines.quantity", "product_uom_qty"
    )
    def _compute_qty_invoiced(self):
        res = super()._compute_qty_invoiced()
        for line in self:
            if line.product_id and not line.product_id.billable:
                line.qty_invoiced = line.product_uom_qty
        return res

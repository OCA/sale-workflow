from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "order_line.qty_delivered", "order_line.qty_invoiced", "order_line.price_unit"
    )
    def _compute_sum_outstanding(self):
        for order in self:
            lines = order.order_line.mapped(
                lambda r: (r.qty_delivered * r.price_unit)
                - (r.qty_invoiced * r.price_unit)
            )
            order["sum_outstanding"] = -sum(lines)

    sum_outstanding = fields.Monetary(
        "Sum Outstanding",
        readonly=True,
        store=True,
        compute="_compute_sum_outstanding",
    )

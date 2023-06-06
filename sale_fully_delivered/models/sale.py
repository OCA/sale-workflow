from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_fully_delivered = fields.Boolean(
        compute="_compute_is_fully_delivered", store=True, index=True
    )

    @api.depends("order_line.qty_delivered")
    def _compute_is_fully_delivered(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for sale in self:
            if all(
                float_compare(
                    line.product_uom_qty, line.qty_delivered, precision_digits=precision
                )
                != 1
                for line in sale.order_line.filtered(
                    lambda l: l._include_in_fully_delivered_compute()
                )
            ):
                sale.is_fully_delivered = True
            else:
                sale.is_fully_delivered = False

# Copyright 2018 Okia SPRL
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_qty_canceled = fields.Float(
        "Qty canceled", readonly=True, copy=False, digits="Product Unit of Measure"
    )
    product_qty_remains_to_deliver = fields.Float(
        string="Remains to deliver",
        digits="Product Unit of Measure",
        compute="_compute_product_qty_remains_to_deliver",
        store=True,
    )
    can_cancel_remaining_qty = fields.Boolean(
        compute="_compute_can_cancel_remaining_qty"
    )

    @api.depends("product_qty_remains_to_deliver", "state")
    def _compute_can_cancel_remaining_qty(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for rec in self:
            rec.can_cancel_remaining_qty = (
                float_compare(
                    rec.product_qty_remains_to_deliver, 0, precision_digits=precision
                )
                == 1
                and rec.state == "done"
                and rec.move_ids
            )

    @api.depends(
        "product_uom_qty",
        "qty_delivered",
        "product_qty_canceled",
    )
    def _compute_product_qty_remains_to_deliver(self):
        for line in self:
            remaining_to_deliver = (
                line.product_uom_qty - line.qty_delivered - line.product_qty_canceled
            )
            line.product_qty_remains_to_deliver = remaining_to_deliver

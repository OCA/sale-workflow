# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_delivered_method = fields.Selection(selection_add=[("delivery", "Delivery")])

    def _is_delivered_method_delivery(self):
        self.ensure_one()
        service_type = self.product_id.service_type
        return (
            self.product_id.type == "service"
            and (not service_type or service_type == "manual")
            and self.product_id.invoice_policy == "delivery"
        )

    def _compute_qty_delivered_method(self):
        super()._compute_qty_delivered_method()
        for line in self:
            if line._is_delivered_method_delivery():
                line.qty_delivered_method = "delivery"

    def _get_delivery_qty_delivered(self):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        qty_delivered = 0
        contains_stock_move_sale_line = False
        is_delivered = False
        for line in self.order_id.order_line:
            if (
                line.qty_delivered_method != "stock_move"
                or line.product_id.invoice_policy != "delivery"
            ):
                continue
            contains_stock_move_sale_line = True
            if not float_is_zero(line.qty_delivered, precision):
                is_delivered = True
                break
        # Only return a delivered qty if there is something delivered
        # or if the sale.order does not contains a sale.order.line
        # with a delivered_method = stock_move
        if is_delivered or not contains_stock_move_sale_line:
            qty_delivered = self.product_uom_qty
        return qty_delivered

    def _compute_qty_delivered_delivery_method(self):
        for line in self.order_id.order_line:
            if line.qty_delivered_method != "delivery":
                continue
            line.qty_delivered = line._get_delivery_qty_delivered()

    def _compute_qty_delivered(self):
        super()._compute_qty_delivered()
        self._compute_qty_delivered_delivery_method()

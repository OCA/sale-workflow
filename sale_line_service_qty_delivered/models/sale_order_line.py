# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_is_zero, groupby


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_delivered_method = fields.Selection(selection_add=[("delivery", "Delivery")])

    def _is_delivered_method_delivery(self):
        self.ensure_one()
        return (
            self.product_id.type == "service"
            and self.product_id.invoice_policy == "delivery"
        )

    def _compute_qty_delivered_method(self):
        super(SaleOrderLine, self)._compute_qty_delivered_method()
        for line in self:
            if line._is_delivered_method_delivery():
                line.qty_delivered_method = "delivery"

    def _get_delivery_qty_delivered(self, delivered):
        self.ensure_one()
        if delivered:
            return self.product_uom_qty
        return 0.0

    def _compute_qty_delivered_delivery_method(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        lines_grouped = groupby(self, lambda l: l.order_id)
        for order, lines in lines_grouped:
            lines = dict(groupby(order.order_line, lambda l: l.qty_delivered_method))
            if "delivery" not in lines:
                continue
            if "stock_move" not in lines:
                delivered = True
            else:
                delivered = any(
                    not float_is_zero(line.qty_delivered, precision)
                    for line in lines["stock_move"]
                )
            for line in lines["delivery"]:
                line.qty_delivered = line._get_delivery_qty_delivered(delivered)

    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()
        self._compute_qty_delivered_delivery_method()

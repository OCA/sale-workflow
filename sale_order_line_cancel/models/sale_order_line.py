# Copyright 2018 Okia SPRL
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2020 ACSONE SA/NV
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
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
            rec.can_cancel_remaining_qty = float_compare(
                rec.product_qty_remains_to_deliver, 0, precision_digits=precision
            ) == 1 and rec.state in ("sale", "done")

    @api.depends(
        "product_uom_qty",
        "qty_delivered",
        "product_qty_canceled",
    )
    def _compute_product_qty_remains_to_deliver(self):
        for line in self:
            qty_to_deliver = line.product_uom_qty - line.qty_delivered
            qty_remaining = max(0, qty_to_deliver - line.product_qty_canceled)
            line.product_qty_remains_to_deliver = qty_remaining

    def write(self, values):
        # When the ordered qty is raised again after some qty was canceled,
        # give the canceled qty back so the line becomes deliverable again.
        # This must happen before super() so the qty is already restored when
        # the procurement (and any resulting move merge/cancel) runs.
        if "product_uom_qty" in values and "product_qty_canceled" not in values:
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            new_qty = values["product_uom_qty"]
            for line in self:
                increase = new_qty - line.product_uom_qty
                if (
                    line.company_id.on_sale_line_cancel_decrease_line_qty
                    and float_compare(
                        line.product_qty_canceled, 0, precision_digits=precision
                    )
                    > 0
                    and float_compare(increase, 0, precision_digits=precision) > 0
                ):
                    line.product_qty_canceled = max(
                        0, line.product_qty_canceled - increase
                    )
        return super().write(values)

    def _update_qty_canceled(self):
        """Update SO line qty canceled only when all remaining moves are canceled"""
        for line in self:
            qty_to_deliver = line.product_uom_qty - line.qty_delivered
            vals = {"product_qty_canceled": qty_to_deliver}
            if (
                line.state == "sale"
                and line.company_id.on_sale_line_cancel_decrease_line_qty
            ):
                vals["product_uom_qty"] = line.qty_delivered
            line.write(vals)

    def cancel_remaining_qty(self):
        lines = self.filtered(lambda l: l.can_cancel_remaining_qty)
        lines._update_qty_canceled()
        for line in lines:
            line.order_id.message_post(
                body=_(
                    "<b>%(product)s</b>: The order line has been canceled",
                    product=line.product_id.display_name,
                )
            )
        return lines

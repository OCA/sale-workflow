# Copyright 2018 Okia SPRL
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2020 ACSONE SA/NV
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
            rec.can_cancel_remaining_qty = (
                float_compare(
                    rec.product_qty_remains_to_deliver, 0, precision_digits=precision
                )
                == 1
                and rec.state in ("sale", "done")
                and rec.qty_delivered_method == "stock_move"
            )

    @api.depends(
        "product_uom_qty",
        "qty_delivered",
        "product_qty_canceled",
    )
    def _compute_product_qty_remains_to_deliver(self):
        for line in self:
            qty_remaining = line.qty_to_deliver - line.product_qty_canceled
            line.product_qty_remains_to_deliver = qty_remaining

    def _get_moves_to_cancel(self):
        return self.move_ids.filtered(lambda m: m.state not in ("done", "cancel"))

    def _check_moves_to_cancel(self, moves):
        """Override this method to add checks before cancel"""
        self.ensure_one()

    def _update_qty_canceled(self):
        """Update SO line qty canceled only when all remaining moves are canceled"""
        for line in self:
            if line._get_moves_to_cancel():
                continue
            line.product_qty_canceled = line.qty_to_deliver

    def cancel_remaining_qty(self):
        lines = self.filtered(lambda l: l.can_cancel_remaining_qty)
        for line in lines:
            moves_to_cancel = line._get_moves_to_cancel()
            line._check_moves_to_cancel(moves_to_cancel)
            moves_to_cancel._action_cancel()
            line.order_id.message_post(
                body=_(
                    "<b>%(product)s</b>: The order line has been canceled",
                    product=line.product_id.display_name,
                )
            )
            return True

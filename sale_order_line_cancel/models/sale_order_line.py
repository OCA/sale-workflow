# Copyright 2018 Okia SPRL
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools import float_compare, float_is_zero


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

    def _get_moves_to_cancel(self):
        return self.move_ids.filtered(lambda m: m.state not in ("done", "cancel"))

    def _check_moves_to_cancel(self, moves):
        """override this method to add checks before cancel"""
        self.ensure_one()

    def cancel_remaining_qty(self):
        lines = self.filtered(lambda l: l.can_cancel_remaining_qty)
        for line in lines:
            moves_to_cancel = line._get_moves_to_cancel()
            line._check_moves_to_cancel(moves_to_cancel)
            line._cancel_by_running_procurement()
            line.order_id.message_post(
                body=_(
                    "<b>%(product)s</b>: The order line has been canceled",
                    product=line.product_id.display_name,
                )
            )
            return True

    def _cancel_by_running_procurement(self):
        """Cancel the remaining quantity by running a new procurement

        To cancel qty to deliver, we'll run the procurement to decrease the
        quantity to deliver. This will be achieved by triggering the
        `_action_launch_stock_rule` by pretending that we previously asked
        for more quantity to deliver than we actually did. This way, the
        system will create a new procurement to deliver a negative quantity.
        As result, stock moves with negative quantity will be created and, if
        possible, be merged with the existing ones.

        When want to cancel the remaining quantity to deliver the method will
        pretend that we previously asked for the sum of the ordered quantity
        and the remaining quantity. This way, the system will at the end create
        the rules to decrease of the remaining quantity.
        (ordered qty + remaining qty - ordered qty = remaining qty)


        :param only_remaining: if True, only the remaining quantity will be
            canceled. If False, the full quantity will be canceled.

        """
        qty_to_cancel = self.product_qty_remains_to_deliver
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if float_is_zero(qty_to_cancel, precision_digits=precision):
            return
        simulate_procured_qty = self.product_uom_qty + qty_to_cancel
        self.ensure_one()
        line = self.with_context(simulate_procured_qty=simulate_procured_qty)
        previous_sate = line.state
        line.state = "sale"
        line._action_launch_stock_rule(simulate_procured_qty)
        line.state = previous_sate
        line.product_qty_canceled += qty_to_cancel

    def _get_qty_procurement(self, previous_product_uom_qty=False):
        return self.env.context.get(
            "simulate_procured_qty",
            super()._get_qty_procurement(previous_product_uom_qty),
        )

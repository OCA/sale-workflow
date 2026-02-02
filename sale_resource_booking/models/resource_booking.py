# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResourceBooking(models.Model):
    _inherit = "resource.booking"

    sale_order_line_id = fields.Many2one(
        "sale.order.line",
        string="Sale order line",
        copy=False,
        index=True,
        ondelete="cascade",
        tracking=True,
    )
    sale_order_id = fields.Many2one(
        related="sale_order_line_id.order_id",
        readonly=True,
        help="Sale order that origins this booking.",
    )
    sale_order_state = fields.Selection(
        string="Sale order state",
        related="sale_order_id.state",
        readonly=True,
        help=(
            "If there is a related quotation and it is not confirmed, "
            "the booking will not be able to become confirmed."
        ),
    )

    @api.depends(
        "active", "meeting_id.attendee_ids.state", "sale_order_line_id.order_id.state"
    )
    def _compute_state(self):
        """A booking can only be confirmed if its sale order is confirmed.

        Note: when buying online, the SO is automatically confirmed when paid,
        which makes this actually move the booking from scheduled to confirmed
        automatically after payment.
        """
        result = super()._compute_state()
        # False means "no sale order"
        confirmable_states = {False, "sale", "done"}
        for one in self:
            # Only affect confirmed bookings related to unconfirmed quotations
            if one.state != "confirmed" or one.sale_order_state in confirmable_states:
                continue
            # SO is not confirmed; neither is booking
            one.state = "scheduled"
        return result

# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tests.common import Form


class SaleOrderBookingConfirm(models.TransientModel):
    _name = "sale.order.booking.confirm"
    _description = "Confirmation dialog to autofill resource bookings"

    order_id = fields.Many2one(
        "sale.order",
        string="Order",
        index=True,
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    resource_booking_ids = fields.One2many(
        related="order_id.order_line.resource_booking_ids", readonly=False
    )

    def action_invite(self):
        """Invite booking requesters."""
        for booking in self.resource_booking_ids:
            share_f = Form(
                self.env["portal.share"].with_context(
                    active_id=booking.id,
                    active_ids=booking.ids,
                    active_model="resource.booking",
                    default_note=booking.requester_advice,
                    default_partner_ids=[(4, booking.partner_id.id, 0)],
                )
            )
            share = share_f.save()
            share.action_send_mail()

    def action_noop(self):
        # At this point, the record was already created with the required
        # changes; nothing left to do
        return

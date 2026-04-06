# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models
from odoo.tests.common import Form


class SaleOrderBookingConfirm(models.TransientModel):
    _name = "sale.order.booking.confirm"
    _description = "Confirmation dialog to autofill resource bookings"

    @api.model
    def _default_resource_booking_ids(self):
        order = self.env["sale.order"].browse(self.env.context.get("default_order_id"))
        return order.order_line.mapped("resource_booking_ids")

    order_id = fields.Many2one(
        "sale.order",
        string="Order",
        index=True,
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    resource_booking_ids = fields.Many2many(
        "resource.booking",
        "sale_order_booking_confirm_resource_booking_rel",
        "sale_order_booking_confirm_id",
        "resource_booking_id",
        string="Bookings",
        default=_default_resource_booking_ids,
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
                    default_partner_ids=[Command.link(booking.partner_id.id)],
                )
            )
            share = share_f.save()
            share.action_send_mail()
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_noop(self):
        # At this point, the record was already created with the required
        # changes; nothing left to do
        return {"type": "ir.actions.client", "tag": "reload"}

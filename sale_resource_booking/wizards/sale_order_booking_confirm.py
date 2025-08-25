# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
        "sale_order_booking_confirm_rel",
        "sale_order_booking_confirm_id",
        "booking_id",
        string="Bookings",
        default=_default_resource_booking_ids,
    )

    def action_invite(self):
        """Invite booking requesters without using odoo.tests.Form."""
        portal_share = self.env["portal.share"]

        for booking in self.resource_booking_ids:
            rec_ctx = dict(
                active_id=booking.id,
                active_ids=[booking.id],
                active_model="resource.booking",
            )
            fields_to_get = list(portal_share._fields)
            vals = portal_share.with_context(**rec_ctx).default_get(fields_to_get)
            vals.update(
                {
                    "res_model": "resource.booking",
                    "res_id": booking.id,
                    "note": booking.requester_advice or "",
                    "partner_ids": [(6, 0, [booking.partner_id.id])]
                    if booking.partner_id
                    else [],
                }
            )
            rec = portal_share.with_context(**rec_ctx).new(vals)
            create_vals = rec._convert_to_write(rec._cache)
            share = portal_share.create(create_vals)
            share.action_send_mail()

        return {"type": "ir.actions.client", "tag": "reload"}

    def action_noop(self):
        # At this point, the record was already created with the required
        # changes; nothing left to do
        return {"type": "ir.actions.client", "tag": "reload"}

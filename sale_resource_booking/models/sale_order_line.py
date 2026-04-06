# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    resource_booking_ids = fields.One2many(
        "resource.booking",
        "sale_order_line_id",
        string="Resource bookings",
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result._sync_resource_bookings()
        return result

    def write(self, vals):
        result = super().write(vals)
        self._sync_resource_bookings()
        return result

    @api.model
    def _bookings_usefulness_index(self, booking):
        """Help knowing how useful would be a booking."""
        by_state = {"confirmed": 100, "scheduled": 200, "pending": 300, "canceled": 400}
        return by_state[booking.state]

    @api.model
    def _add_or_cancel_bookings(self, bookings, qty, values):
        """Apply the desired state to the selected bookings set.

        :param bookings: Recordset representing the bookings to modify.
        :param int qty: Amount of bookings that should exist in the set.
        :param dict values: Values to write/create on bookings.
        :return: Recordset with all bookings, including any new one created.
        """
        qty = max(qty, 0)  # Negative qty means zero bookings
        bookings = bookings.sorted(self._bookings_usefulness_index)
        useful, useless = bookings[:qty], bookings[qty:]
        # Cancel useless bookings
        useless.action_cancel()
        # Update useful bookings
        useful.write(dict(values, active=True))
        # Create missing bookings
        bookings |= self.env["resource.booking"].create(
            [dict(values) for _n in range(qty - len(useful))]
        )
        return bookings

    def _sync_resource_bookings(self):
        """Sync related resource booking records."""
        # Sudo because user maybe does not have resource booking permissions,
        # but still he should be able to sync bookings
        for line in self.sudo().with_context(active_test=False):
            bookings = line.resource_booking_ids
            # No bookings for products not related to RBT, or canceled orders
            if not line.product_id.resource_booking_type_id or line.state == "cancel":
                line._add_or_cancel_bookings(bookings, 0, {})
                continue
            # Only link bookings for orders, or when forced
            if not line.env.context.get("force_bookings_sync") and (
                not line.product_id.resource_booking_type_id or line.state != "sale"
            ):
                continue
            values = {
                "sale_order_line_id": line.id,
                "type_id": line.product_id.resource_booking_type_id.id,
            }
            rbc_rel = line.product_id.resource_booking_type_combination_rel_id
            context = {
                "default_partner_id": line.order_id.partner_id.id,
                "default_combination_auto_assign": not rbc_rel,
                "default_combination_id": rbc_rel.combination_id.id,
            }
            line.with_context(**context)._add_or_cancel_bookings(
                bookings, int(line.product_uom_qty), values
            )

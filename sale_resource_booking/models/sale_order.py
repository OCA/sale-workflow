# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    resource_booking_ids = fields.Many2many(
        "resource.booking", compute="_compute_resource_bookings"
    )
    resource_booking_count = fields.Integer(
        "Resource bookings count", compute="_compute_resource_bookings"
    )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result.mapped("order_line")._sync_resource_bookings()
        return result

    def write(self, vals):
        result = super().write(vals)
        if "state" in vals:
            self.mapped("order_line")._sync_resource_bookings()
        return result

    @api.depends("order_line.resource_booking_ids")
    def _compute_resource_bookings(self):
        for one in self:
            bookings = one.mapped("order_line.resource_booking_ids")
            one.resource_booking_ids = bookings
            one.resource_booking_count = len(bookings)

    def action_open_resource_bookings(self):
        """Open related bookings."""
        result = {
            "domain": [("sale_order_id", "=", self.id)],
            "name": _("Bookings"),
            "res_model": "resource.booking",
            "target": "current",
            "type": "ir.actions.act_window",
            "view_mode": "list,calendar,form",
        }
        return result

    def action_confirm(self):
        """Ask to fill booking values, if necessary."""
        result = super().action_confirm()
        try:
            # Only open wizard if doing this from a single record with bookings
            if len(self) > 1 or not self.resource_booking_ids:
                return result
        except exceptions.AccessError:
            # User without access to resource.booking; no confirm wizard
            return result
        # Support chained actions, like when event_sale is installed
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_resource_booking.sale_order_booking_confirm_action"
        )
        action["context"] = {"default_order_id": self.id}
        actions = [action]
        if isinstance(result, dict):
            actions.insert(0, result)
        return {"type": "ir.actions.act_multi", "actions": actions}

    def action_bookings_resync(self):
        """User-forced bookings resync."""
        self.with_context(force_bookings_sync=True).order_line._sync_resource_bookings()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_resource_booking.sale_order_booking_confirm_action"
        )
        action["context"] = {"default_order_id": self.id}
        return action

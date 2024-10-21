# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PartnerDeliveryZone(models.Model):
    _name = "partner.delivery.zone"
    _inherit = ["partner.delivery.zone", "time.cutoff.mixin"]

    order_delivery_cutoff_preference = fields.Selection(
        [
            ("warehouse_cutoff", "Use global (warehouse) cutoff time"),
            ("partner_cutoff", "Use partner's cutoff time"),
        ],
        string="Delivery orders cutoff preference",
        default="warehouse_cutoff",
        help="Define the cutoff time for delivery orders:\n\n"
        "* Use global (warehouse) cutoff time: Delivery order for sale orders"
        " will be postponed to the next warehouse cutoff time\n"
        "* Use partner's cutoff time: Delivery order for sale orders"
        " will be postponed to the next partner's cutoff time\n\n"
        "Example: If cutoff is set to 09:00, any sale order confirmed before "
        "09:00 will have its delivery order postponed to 09:00, and any sale "
        "order confirmed after 09:00 will have its delivery order postponed "
        "to 09:00 on the following day.",
    )

    delivery_time_preference = fields.Selection(
        [
            ("anytime", "Any time"),
            ("time_windows", "Fixed time windows"),
            ("workdays", "Weekdays (Monday to Friday)"),
        ],
        string="Delivery time schedule preference",
        default="anytime",
        required=True,
        help="Define the scheduling preference for delivery orders:\n\n"
        "* Any time: Do not postpone deliveries\n"
        "* Fixed time windows: Postpone deliveries to the next preferred "
        "time window\n"
        "* Weekdays: Postpone deliveries to the next weekday",
    )

    delivery_time_window_ids = fields.One2many(
        "zone.delivery.time.window",
        "delivery_zone_id",
        string="Delivery time windows",
    )

    @api.constrains("delivery_time_preference", "delivery_time_window_ids")
    def _check_delivery_time_preference(self):
        for zone in self:
            if (
                zone.delivery_time_preference == "time_windows"
                and not zone.delivery_time_window_ids
            ):
                raise ValidationError(
                    _(
                        "Please define at least one delivery time window or change"
                        " preference to Any time"
                    )
                )

# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ZoneDeliveryTimeWindow(models.Model):
    _name = "zone.delivery.time.window"
    _inherit = "time.window.mixin"
    _description = "Preferred delivery time windows for a delivery zone"

    _time_window_overlap_check_field = "delivery_zone_id"

    delivery_zone_id = fields.Many2one(
        "partner.delivery.zone", required=True, index=True, ondelete="cascade"
    )

    @api.constrains("delivery_zone_id")
    def check_window_no_overlaps(self):
        return super().check_window_no_overlaps()

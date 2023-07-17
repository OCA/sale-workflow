# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("delivery_zone_id")
    def _onchange_delivery_zone_id(self):
        if self.delivery_zone_id:
            zone = self.delivery_zone_id
            self.order_delivery_cutoff_preference = (
                zone.order_delivery_cutoff_preference
            )
            if self.order_delivery_cutoff_preference == "partner_cutoff":
                self.cutoff_time = zone.cutoff_time
            else:
                self.cutoff_time = False

            self.delivery_time_preference = zone.delivery_time_preference
            if self.delivery_time_preference == "time_windows":
                time_windows = []
                for tw in zone.delivery_time_window_ids:
                    time_windows.append(
                        (
                            0,
                            0,
                            {
                                "time_window_start": tw.time_window_start,
                                "time_window_end": tw.time_window_end,
                                "time_window_weekday_ids": tw.time_window_weekday_ids.ids,
                            },
                        )
                    )
                self.delivery_time_window_ids = time_windows
            else:
                self.delivery_time_window_ids = False

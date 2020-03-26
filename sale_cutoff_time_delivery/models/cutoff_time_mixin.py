# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class CutoffTimeMixin(models.AbstractModel):

    _name = "cutoff.time.mixin"

    order_delivery_cutoff_hours = fields.Selection(
        selection="_selection_order_delivery_cutoff_hours", required=True, default="12"
    )
    order_delivery_cutoff_minutes = fields.Selection(
        selection="_selection_order_delivery_cutoff_minutes",
        required=True,
        default="00",
    )

    @api.model
    def _selection_order_delivery_cutoff_hours(self):
        return [("{:02}".format(i), "{:02}".format(i)) for i in range(0, 24)]

    @api.model
    def _selection_order_delivery_cutoff_minutes(self):
        return [("{:02}".format(i), "{:02}".format(i)) for i in range(0, 60)]

    def get_cutoff_time(self):
        return {
            "hour": self.order_delivery_cutoff_hours,
            "minute": self.order_delivery_cutoff_minutes,
        }

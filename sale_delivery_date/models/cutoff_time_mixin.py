# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import math
from datetime import time

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import _tz_get


class TimeCutoffMixin(models.AbstractModel):

    _name = "time.cutoff.mixin"
    _description = "Time Cut-off Mixin"

    cutoff_time = fields.Float()
    tz = fields.Selection(_tz_get, string="Timezone")

    def get_cutoff_time(self):
        hour, minute = self._get_hour_min_from_value(self.cutoff_time)
        return {
            "hour": hour,
            "minute": minute,
            "tz": self.tz,
        }

    @api.model
    def _get_hour_min_from_value(self, value):
        hour = math.floor(value)
        minute = round((value % 1) * 60)
        if minute == 60:
            minute = 0
            hour += 1
        return hour, minute

    @api.model
    def float_to_time_repr(self, value):
        pattern = "%02d:%02d"
        hour, minute = self._get_hour_min_from_value(value)
        return pattern % (hour, minute)

    @api.model
    def float_to_time(self, value):
        hour, minute = self._get_hour_min_from_value(value)
        return time(hour=hour, minute=minute)

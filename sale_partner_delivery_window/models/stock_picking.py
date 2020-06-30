# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import timedelta

from odoo import _, api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _planned_delivery_date(self):
        res = super()._planned_delivery_date()
        sec_lead_time = self.company_id.security_lead
        if sec_lead_time:
            res += timedelta(days=sec_lead_time)
        return self.scheduled_date

    @api.onchange("scheduled_date")
    def _onchange_scheduled_date(self):
        res = super()._onchange_scheduled_date()
        if res and "warning" in res:
            sec_lead_time = self.company_id.security_lead
            if sec_lead_time:
                res["warning"]["message"] += _(
                    "\nConsidering the security lead time of %s days defined on "
                    "the company, the delivery will not match the partner time"
                    "windows preference." % sec_lead_time
                )

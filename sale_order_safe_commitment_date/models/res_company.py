# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from datetime import datetime, time

import pytz
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sales_cutoff_calendar = fields.Many2one(
        comodel_name="resource.calendar",
        string="Sales cut-off schedule",
    )
    in_sale_cutoff_hour = fields.Boolean(
        compute="_compute_in_sale_cutoff_hour",
        help="Sales can't be delivered according to their lead times and will be "
        "postponed for a day",
    )

    def _get_cutoff_intervals(self, now, range_end):
        self.ensure_one()
        return sorted(
            self.sales_cutoff_calendar._work_intervals_batch(
                now, range_end, self.env["resource.resource"]
            )[False],
            key=lambda i, now=now: abs(i[0] - now),
        )

    def _days_to_deliver(self, date, days=30):
        """Based on the cut-off calendar, when is the next day I can deliver"""
        # Maybe we'll have to separate the cut-off calendar from the delivery calendar
        self.ensure_one()
        # Nothing to compute
        if not self.sales_cutoff_calendar:
            return 0
        from_date = datetime.combine(
            date, time.min, tzinfo=pytz.timezone(self.env.user.tz or "UTC")
        )
        intervals = self._get_cutoff_intervals(
            from_date, from_date + relativedelta(days=days)
        )
        # We don't really know, really. Maybe could set some recurrence to findout
        # the exact days...
        if not intervals:
            return days + 1
        return (intervals[0][0] - from_date).days

    def _compute_in_sale_cutoff_hour(self):
        self.in_sale_cutoff_hour = False
        now = self.env.context.get("sale_cutoff_datetime")
        for company in self.filtered("sales_cutoff_calendar"):
            if not now:
                now = fields.Datetime.now().replace(tzinfo=pytz.utc)
            now = now.astimezone(pytz.timezone(self.env.user.tz or "UTC"))
            range_end = now + relativedelta(days=1, hour=0, minute=0, second=0)
            interval = company._get_cutoff_intervals(now, range_end)
            if interval:
                # We're inside the sales period
                company.in_sale_cutoff_hour = bool(interval[0][0] - now)
            else:
                company.in_sale_cutoff_hour = True

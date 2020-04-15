# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import datetime, timedelta

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.date_utils import date_range


class ResPartner(models.Model):

    _inherit = "res.partner"

    def next_delivery_window_start_datetime(self, from_date=None, timedelta_days=None):
        """Returns the next starting datetime in a preferred delivery window.
        If from_date is already in a delivery window, from_date is "the next"

        :param from_date: Datetime object (Leave empty to use now())
        :param timedelta_days: Number of days to use in the computation
                               (Leave empty to use 7 days or 1 week)
        :return: Datetime object
        """
        self.ensure_one()
        if not from_date:
            from_date = datetime.now()
        if self.is_in_delivery_window(from_date):
            return from_date
        if timedelta_days is None:
            timedelta_days = 7
        datetime_windows = self.get_next_windows_start_datetime(
            from_date, from_date + timedelta(days=timedelta_days)
        )
        for dwin_start in datetime_windows:
            if dwin_start >= from_date:
                return dwin_start
        raise UserError(_("Something went wrong trying to find next delivery window"))

    def get_next_windows_start_datetime(self, from_datetime, to_datetime):
        """Returns all delivery windows start time from the from_datetime weekday
        to the to_datetime weekday.
        Note result can include a start datetime that is before from_datetime
        on the from_datetime weekday

        :param from_datetime: Datetime object
        :param to_datetime: Datetime object
        :return: List of Datetime objects
        """
        res = list()
        for this_datetime in date_range(from_datetime, to_datetime, timedelta(days=1)):
            this_weekday_number = this_datetime.weekday()
            this_weekday = self.env["time.weekday"].search(
                [("name", "=", this_weekday_number)], limit=1
            )
            # Sort by start time to ensure the window we'll find will be the first
            # one for the weekday
            this_weekday_windows = self.delivery_time_window_ids.filtered(
                lambda w: this_weekday in w.time_window_weekday_ids
            ).sorted("time_window_start")
            for win in this_weekday_windows:
                this_weekday_start_datetime = datetime.combine(
                    this_datetime, win.get_time_window_start_time()
                )
                res.append(this_weekday_start_datetime)
        return res

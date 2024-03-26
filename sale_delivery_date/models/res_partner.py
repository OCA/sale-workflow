# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime, timedelta

from pytz import timezone, utc

from odoo import _, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.date_utils import date_range

from odoo.addons.partner_tz.tools import tz_utils


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "time.cutoff.mixin"]

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

    def next_delivery_window_start_datetime(self, from_date=None, timedelta_days=None):
        """Get next starting datetime in a preferred delivery window.

        If from_date is already in a delivery window, from_date is "the next"

        :param from_date: Datetime object (Leave empty to use now())
        :param timedelta_days: Number of days to use in the computation
                               (Leave empty to use 7 days or 1 week)
        :return: Datetime object
        """
        if not from_date:
            from_date = datetime.now()
        if not self:
            return from_date
        if self.is_in_delivery_window(from_date):
            return from_date
        if timedelta_days is None:
            timedelta_days = 7
        if self.delivery_time_preference == "workdays":
            # TODO tz
            datetime_windows = self.get_next_workdays_datetime(
                from_date, from_date + timedelta(days=timedelta_days)
            )
        else:
            datetime_windows = self.get_next_windows_start_datetime(
                from_date, from_date + timedelta(days=timedelta_days)
            )
        for dwin_start in datetime_windows:
            if dwin_start >= from_date:
                return dwin_start
        raise UserError(
            _("Something went wrong trying to find next delivery window. Date: %s")
            % str(from_date)
        )

    def get_next_workdays_datetime(self, from_datetime, to_datetime):
        """Returns all the delivery windows in the provided date range.

        :param from_datetime: Datetime object
        :param to_datetime: Datetime object
        :return: List of Datetime objects
        """
        # Converting input dates as customer's tz here, as weekday might change
        # during the conversion
        tz_string = self.tz or self.env.company.partner_id.tz or "UTC"
        tz = timezone(tz_string)
        from_datetime_utc = utc.localize(from_datetime)
        from_datetime_tz = from_datetime_utc.astimezone(tz)
        to_datetime_utc = utc.localize(to_datetime)
        to_datetime_tz = to_datetime_utc.astimezone(tz)
        dates = date_range(from_datetime_tz, to_datetime_tz, timedelta(days=1))
        return [
            # returns naive utc datetimes
            date.astimezone(utc).replace(tzinfo=None)
            for date in dates
            if date.weekday() < 5
        ]

    @tools.ormcache("weekday_number")
    def _get_weekday(self, weekday_number):
        return self.env["time.weekday"].search(
            [("name", "=", weekday_number)], limit=1
        )

    def get_next_windows_start_datetime(self, from_datetime, to_datetime):
        """Get all delivery windows start time.

        Range from from_datetime weekday to to_datetime weekday.

        Note result can include a start datetime that is before from_datetime
        on the from_datetime weekday
        Note 2 time windows are in the context of customer's tz.
        We have to localize from_date, to_datetime first, and return a naive
        UTC datetime.

        :param from_datetime: Datetime object
        :param to_datetime: Datetime object
        :return: List of Datetime objects
        """
        res = list()
        tz_string = self.tz or self.env.company.partner_id.tz or "UTC"
        tz = timezone(tz_string)
        from_datetime_utc = utc.localize(from_datetime)
        from_datetime_tz = from_datetime_utc.astimezone(tz)
        to_datetime_utc = utc.localize(to_datetime)
        to_datetime_tz = to_datetime_utc.astimezone(tz)
        for this_datetime in date_range(
            from_datetime_tz, to_datetime_tz, timedelta(days=1)
        ):
            this_weekday_number = this_datetime.weekday()
            this_weekday = self._get_weekday(this_weekday_number)
            # Sort by start time to ensure the window we'll find will be the first
            # one for the weekday
            this_weekday_windows = self.delivery_time_window_ids.filtered(
                lambda w: this_weekday in w.time_window_weekday_ids
            ).sorted("time_window_start")
            for win in this_weekday_windows:
                this_weekday_start_datetime = datetime.combine(
                    this_datetime, win.get_time_window_start_time()
                )
                # this_weekday_start_datetime is a naive datetime in the context
                # of customer's tz.
                # Convert is to UTC, then make it naive
                weekday_start_utc_naive = tz_utils.tz_to_utc_naive_datetime(
                    tz, this_weekday_start_datetime
                )
                res.append(weekday_start_utc_naive)
        return res

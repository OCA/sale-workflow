# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import calendar
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

WEEKDAY_MAPPING = {
    "0": "monday",
    "1": "tuesday",
    "2": "wednesday",
    "3": "thursday",
    "4": "friday",
    "5": "saturday",
    "6": "sunday",
}


class ResPartner(models.Model):

    _inherit = "res.partner"

    delivery_schedule_preference = fields.Selection(
        [("direct", "As soon as possible"), ("fix_weekdays", "Fixed week days")],
        string="Delivery schedule preference",
        default="direct",
        required=True,
        help="Define the scheduling preference for delivery orders:\n\n"
        "* As soon as possible: Do not postpone deliveries\n"
        "* Fixed week days: Postpone deliveries to the next preferred "
        "weekday",
    )

    delivery_schedule_monday = fields.Boolean(default=True, string="Monday")
    delivery_schedule_tuesday = fields.Boolean(default=True, string="Tuesday")
    delivery_schedule_wednesday = fields.Boolean(default=True, string="Wednesday")
    delivery_schedule_thursday = fields.Boolean(default=True, string="Thursday")
    delivery_schedule_friday = fields.Boolean(default=True, string="Friday")
    delivery_schedule_saturday = fields.Boolean(default=True, string="Saturday")
    delivery_schedule_sunday = fields.Boolean(default=True, string="Sunday")

    @api.constrains(
        "delivery_schedule_preference",
        "delivery_schedule_monday",
        "delivery_schedule_tuesday",
        "delivery_schedule_wednesday",
        "delivery_schedule_thursday",
        "delivery_schedule_friday",
        "delivery_schedule_saturday",
        "delivery_schedule_sunday",
    )
    def _check_delivery_schedule(self):
        """Ensure at least one preferred day is defined"""
        days_fields = ["delivery_schedule_%s" % d.lower() for d in calendar.day_name]
        for partner in self:
            if partner.delivery_schedule_preference == "fix_weekdays" and not any(
                [partner[d] for d in days_fields]
            ):
                raise ValidationError(
                    _(
                        "At least one preferred weekday must be defined if "
                        "partner is set as 'Fixed week days' deliveries."
                    )
                )

    def get_delivery_schedule_preferred_weekdays(self, translate=False):
        """List preferred weekdays"""
        self.ensure_one()
        if self.delivery_schedule_preference == "direct":
            res = [d.lower() for d in calendar.day_name]
        else:
            res = [
                d.lower()
                for d in calendar.day_name
                if self["delivery_schedule_%s" % d.lower()]
            ]
        if translate:
            fields_tr = self.env['ir.translation'].get_field_string(
                self._name
            )
            res = [fields_tr.get("delivery_schedule_%s" % day) for day in res]
        return res

    def _next_delivery_schedule_preferred_date(self, date_time=None):
        """Returns next preferred date according to weekday preference"""
        self.ensure_one()
        if date_time is None:
            date_time = fields.Datetime.today()
        if not isinstance(date_time, fields.Datetime):
            date_time = fields.Datetime.to_datetime(date_time)
        preferred_weekdays = self.get_delivery_schedule_preferred_weekdays()
        raw_date_weekday = date_time.weekday()
        date_weekday = WEEKDAY_MAPPING.get(str(raw_date_weekday))
        # Check if weekday is allowed
        if (
            date_weekday in preferred_weekdays
            or self.delivery_schedule_preference != 'fix_weekdays'
        ):
            return date_time
        # Iterate over weekdays to find the next one being True
        #  i = number of days to add until next valid weekday
        #  wk_day = possible weekday number (to be converted by modulo 7 below)
        for i, wk_day in enumerate(
            range(raw_date_weekday + 1, raw_date_weekday + 7), 1
        ):
            # Raw target weekday is the day number as returned by weekday method
            raw_target_weekday = wk_day % 7
            target_weekday = WEEKDAY_MAPPING.get(str(raw_target_weekday))
            # As soon as a valid weekday is found, add the number of days
            #  until this weekday
            if target_weekday in preferred_weekdays:
                return date_time + timedelta(days=i)

    def is_preferred_delivery_weekday(self, weekday):
        self.ensure_one()
        return self["delivery_schedule_%s" % weekday]

# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

import pytz

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools.date_utils import relativedelta

# from odoo.addons.calendar.models.calendar import calendar_id2real_id


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    target_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Target partner",
        help="Is the partner used in planner",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency", related="target_partner_id.currency_id"
    )
    hour = fields.Float(compute="_compute_hour", inverse="_inverse_hour")
    target_partner_mobile = fields.Char(related="target_partner_id.mobile")
    sale_planner_calendar_event_id = fields.Many2one(
        comodel_name="sale.planner.calendar.event",
        compute="_compute_sale_planner_calendar_event_id",
    )
    event_planner_state = fields.Char(
        compute="_compute_sale_planner_calendar_event_id",
    )
    # When arrive this date we will unsubscribe user from partner documents
    unsubscribe_date = fields.Date()
    is_dynamic_end_date = fields.Boolean(copy=False)
    # dynamic_end_date = fields.Date(compute="_compute_dynamic_end_date")
    advanced_cycle = fields.Boolean()
    cycle_number = fields.Integer()
    cycle_skip = fields.Integer()
    # Field to know which event creates the recurrence
    is_base_recurrent_event = fields.Boolean(
        compute="_compute_is_base_recurrent_event", store=True
    )

    def _apply_recurrence_values(self, values, future=True):
        """Method to apply recurrence when 'create_recurrence_new_user' key is set on
        the context.
        """
        if not self.env.context.get("create_recurrence_new_user") or not future:
            return super()._apply_recurrence_values(values, future=future)
        to_update = self.env["calendar.recurrence"]
        for event in self:
            to_update |= event.recurrence_id._split_from(event, values)
        self.with_context(create_recurrence_new_user=False).write(
            {"recurrency": True, "follow_recurrence": True}
        )
        return to_update._apply_recurrence()

    @api.depends("recurrence_id", "recurrence_id.base_event_id")
    def _compute_is_base_recurrent_event(self):
        for record in self:
            record.is_base_recurrent_event = (
                record == record.recurrence_id.base_event_id
            )

    @api.depends("start")
    def _compute_hour(self):
        for rec in self:
            date = rec._get_hour_tz_offset()
            rec.hour = date.hour + date.minute / 60

    @api.depends("start", "target_partner_id", "user_id")
    def _compute_sale_planner_calendar_event_id(self):
        # TODO: Adjust order or use [:1] or [-1:] when know model order
        domain = [
            ("calendar_event_date", "in", self.mapped("start")),
            ("partner_id", "in", self.mapped("target_partner_id").ids),
            ("user_id", "=", self.user_id.id),
        ]
        events = self.env["sale.planner.calendar.event"].search(domain)
        for rec in self:
            rec.sale_planner_calendar_event_id = events.filtered(
                lambda r: (
                    r.calendar_event_date == fields.Datetime.to_datetime(rec.start)
                    and r.partner_id == rec.target_partner_id
                    and r.user_id == rec.user_id
                )
            )[:1]
            rec.event_planner_state = rec.sale_planner_calendar_event_id.state

    def _get_hour_tz_offset(self):
        timezone = self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        self_tz = self.with_context(tz=timezone)
        date = fields.Datetime.context_timestamp(self_tz, self.start)
        return date

    def _inverse_hour(self):
        for rec in self:
            duration = rec.duration
            date = self._get_hour_tz_offset()
            new_time = date.replace(
                hour=int(rec.hour), minute=int(round((rec.hour % 1) * 60))
            )
            # Force to onchange get correct value
            new_time = new_time.astimezone(pytz.utc).replace(tzinfo=None)
            rec.write(
                {
                    "recurrence_update": "all_events",
                    "start": new_time,
                    "stop": new_time + timedelta(minutes=round((duration or 0.5) * 60)),
                }
            )

    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get("calendar_event_primary_only", False):
            args = expression.AND([args, [("is_base_recurrent_event", "=", True)]])
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    def _create_event_planner(self):
        return self.env["sale.planner.calendar.event"].create(
            {
                "name": self.name,
                "partner_id": self.target_partner_id.id,
                "user_id": self.user_id.id,
                "calendar_event_date": self.start,
                "calendar_event_id": self.id,
            }
        )

    def get_planner_calendar_event(self):
        return self.sale_planner_calendar_event_id or self._create_event_planner()

    @api.onchange("start", "stop", "duration")
    def _onchange_duration(self):
        """Show warning if duration more than max duration set in config."""
        if not self.target_partner_id:
            return
        max_duration = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_planner_calendar.max_duration",
                default="0.0",
            )
        )
        if max_duration and self.duration > max_duration:
            return {
                "warning": {
                    "title": "Max duration exceeded",
                    "message": "Max duration set in config parameters is {} hours".format(
                        max_duration
                    ),
                    "type": "notification",
                }
            }

    def action_create_sale_order(self):
        """
        Search or Create an event planner  linked to sale order
        """
        planner_event = self.get_planner_calendar_event()
        return planner_event.action_open_sale_order()

    def action_create_event_planner(self):
        planner_event = self.get_planner_calendar_event()
        return planner_event.get_formview_action()

    @api.model
    def cron_update_dynamic_final_date(self):
        events_to_update = self.with_context(calendar_event_primary_only=True).search(
            [("is_dynamic_end_date", "=", True)]
        )
        new_date = fields.Date.today() + relativedelta(
            months=self.env.company.sale_planner_forward_months, day=31
        )
        events_to_update.until = new_date

    def get_week_days_count(self):
        days = ["mo", "tu", "we", "th", "fr", "sa"]
        days_count = 0
        for day in days:
            if self[day]:
                days_count += 1
        return days_count

    def _get_recurrent_dates_by_event(self):
        dates_list = super()._get_recurrent_dates_by_event()
        if not self.advanced_cycle:
            return dates_list
        new_dates = []
        index = 0
        skip_count = 0

        cycle_number = self.cycle_number
        cycle_skip = self.cycle_skip
        if self.rrule_type == "weekly":
            days_count = self.get_week_days_count()
            cycle_number *= days_count
            cycle_skip *= days_count
        for dates in dates_list:
            if index < cycle_number:
                new_dates.append(dates)
                index += 1
            else:
                skip_count += 1
                if skip_count >= cycle_skip:
                    index = 0
                    skip_count = 0
        return new_dates

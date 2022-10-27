# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SalePlannerCalendarWizard(models.TransientModel):
    _name = "sale.planner.calendar.wizard"
    _description = "Sale planner calendar Wizard"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
    )
    event_type_id = fields.Many2one(
        comodel_name="calendar.event.type", string="Event type"
    )
    week_list = fields.Selection(
        [
            ("MON", "Monday"),
            ("TUE", "Tuesday"),
            ("WED", "Wednesday"),
            ("THU", "Thursday"),
            ("FRI", "Friday"),
            ("SAT", "Saturday"),
            ("SUN", "Sunday"),
        ],
        string="Weekday",
    )
    calendar_event_ids = fields.Many2many(
        comodel_name="calendar.event",
        compute="_compute_calendar_event_ids",
        readonly=False,
    )

    @api.depends("user_id", "event_type_id", "week_list")
    def _compute_calendar_event_ids(self):
        for rec in self:
            domain = [
                ("recurrency", "=", True),
                ("recurrence_id.until", ">", fields.Date.today()),
            ]
            if rec.user_id:
                domain.append(("user_id", "=", rec.user_id.id))
            if rec.event_type_id:
                domain.append(("categ_ids", "in", rec.event_type_id.ids))
            if rec.week_list:
                domain.append(("recurrence_id." + rec.week_list.lower(), "=", True))
            rec.calendar_event_ids = (
                self.env["calendar.event"]
                .with_context(calendar_event_primary_only=True)
                .search(domain)
                .sorted("hour")
            )

    # TODO: Remove when control_panel_hidden works
    @api.depends("user_id", "event_type_id")
    def name_get(self):
        result = []
        for wiz in self:
            name = "{} - {}".format(wiz.user_id.name, wiz.event_type_id.name or "Plan")
            result.append((wiz.id, name))
        return result

    def apply(self):
        pass

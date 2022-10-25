# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SalePlannerCalendarSummary(models.Model):
    _name = "sale.planner.calendar.summary"
    _description = "Sale planner calendar summary"
    _inherit = "mail.thread"

    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company.id
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
    )
    date = fields.Date(default=fields.Date.context_today)
    sale_planner_calendar_event_ids = fields.One2many(
        comodel_name="sale.planner.calendar.event",
        inverse_name="calendar_summary_id",
    )
    user_id = fields.Many2one(
        comodel_name="res.users", default=lambda self: self.env.user.id, index=True
    )
    sale_ids = fields.One2many(
        comodel_name="sale.order",
        compute="_compute_sale_ids",
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="pending",
    )
    comment = fields.Text()
    sale_order_subtotal = fields.Monetary(
        compute="_compute_sale_ids", currency_field="currency_id"
    )
    event_type_id = fields.Many2one(
        comodel_name="calendar.event.type",
        string="Event type",
    )
    # Summary data results
    event_total_count = fields.Integer(compute="_compute_event_planner_count")
    event_done_count = fields.Integer(compute="_compute_event_planner_count")
    event_effective_count = fields.Integer(compute="_compute_event_planner_count")
    event_off_planning_count = fields.Integer(compute="_compute_event_planner_count")
    sale_order_count = fields.Integer(compute="_compute_sale_ids")
    payment_count = fields.Integer(compute="_compute_event_planner_count")
    payment_amount = fields.Monetary(compute="_compute_event_planner_count")

    @api.depends("sale_planner_calendar_event_ids")
    def _compute_sale_ids(self):
        for rec in self:
            sales = rec.sale_planner_calendar_event_ids.mapped("sale_ids")
            rec.sale_ids = sales
            rec.sale_order_subtotal = sum(sales.mapped("amount_untaxed"))
            rec.sale_order_count = len(sales)

    @api.depends(
        "sale_planner_calendar_event_ids",
        "sale_planner_calendar_event_ids.state",
        "sale_planner_calendar_event_ids.sale_ids",
        "sale_planner_calendar_event_ids.off_planning",
    )
    def _compute_event_planner_count(self):
        for summary in self:
            event_total_count = 0
            event_done_count = 0
            event_effective_count = 0
            event_off_planning_count = 0
            payment_count = 0
            payment_amount = 0.0
            for event in summary.sale_planner_calendar_event_ids:
                event_total_count += 1
                if event.state == "done":
                    event_done_count += 1
                if event.sale_ids:
                    event_effective_count += 1
                if event.off_planning:
                    event_off_planning_count += 1
                for payment in event.payment_sheet_line_ids:
                    payment_count += 1
                    payment_amount += payment.amount
            summary.event_total_count = event_total_count
            summary.event_done_count = event_done_count
            summary.event_effective_count = event_effective_count
            summary.event_off_planning_count = event_off_planning_count
            summary.payment_count = payment_count
            summary.payment_amount = payment_amount

    @api.constrains("user_id", "date", "event_type_id")
    def _check_existing_summaries(self):
        for rec in self:
            summaries = self.search(
                [
                    ("user_id", "=", rec.user_id.id),
                    ("date", "=", rec.date),
                    ("event_type_id", "=", rec.event_type_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            if summaries:
                raise ValidationError(
                    _(
                        "Already exists a summary with same user, date and event type)\n"
                        "Access with 'Sale planner calendar summary' menu option"
                    )
                )

    def name_get(self):
        res = []
        DateField = self.env["ir.qweb.field.date"]
        for line in self:
            name = "{} {}".format(
                DateField.value_to_html(line.date, {}), line.user_id.name
            )
            res.append((line.id, name))
        return res

    def action_open_sale_order(self):
        """
        Search or Create an event planner linked to sale order
        """
        action = self.env.ref("sale.action_quotations_with_onboarding")
        action = action.read()[0]
        action["context"] = {
            "default_user_id": self.user_id.id,
        }
        if len(self.sale_ids) > 1:
            action["domain"] = [
                (
                    "sale_planner_calendar_event_id",
                    "in",
                    self.sale_planner_calendar_event_ids.ids,
                )
            ]
        else:
            action["views"] = [(self.env.ref("sale.view_order_form").id, "form")]
            action["res_id"] = self.sale_ids.id
        return action

    @api.model
    def action_get_today_summary(self):
        domain = [
            ("user_id", "=", self.env.user.id),
            ("date", "=", fields.Date.today()),
        ]
        summary = self.search(domain)
        action = self.env.ref(
            "sale_planner_calendar.action_sale_planner_calendar_summary"
        ).read()[0]
        if len(summary) > 1:
            action["domain"] = [("id", "in", summary.ids)]
        else:
            action["views"] = [
                (
                    self.env.ref(
                        "sale_planner_calendar.view_sale_planner_calendar_summary_form"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = summary.id
        return action

    def action_done(self):
        self.write(
            {
                "state": "done",
                # "comment": 'Done',
            }
        )

    def action_cancel(self):
        self.write(
            {
                "state": "cancel",
                "comment": "Not done",
            }
        )

    def action_pending(self):
        self.write(
            {
                "state": "pending",
                "comment": False,
            }
        )

    def action_process(self):
        calendar_event_domain = [
            ("start", ">=", self.date.strftime("%Y-%m-%d 00:00:00")),
            ("start", "<=", self.date.strftime("%Y-%m-%d 23:59:59")),
            ("user_id", "=", self.user_id.id),
        ]
        if self.event_type_id:
            calendar_event_domain.append(("categ_ids", "in", self.event_type_id.ids))
        calendar_events = self.env["calendar.event"].search(calendar_event_domain)

        event_planner_domain = [
            ("calendar_event_date", ">=", self.date.strftime("%Y-%m-%d 00:00:00")),
            ("calendar_event_date", "<=", self.date.strftime("%Y-%m-%d 23:59:59")),
            ("user_id", "=", self.user_id.id),
            "|",
            ("calendar_summary_id", "=", False),
            ("calendar_summary_id", "=", self.id),
        ]
        events_planner = self.env["sale.planner.calendar.event"].search(
            event_planner_domain
        )
        # We can not do a typical search due to returned virtual ids like this
        # ("calendar_event_id.categ_ids", "in", self.event_type_id.ids)
        if self.event_type_id:
            events_planner = events_planner.filtered(
                lambda p: self.event_type_id.id in p.calendar_event_id.categ_ids.ids
            )

        for calendar_event in calendar_events:
            event_planner = events_planner.filtered(
                lambda r: r.calendar_event_date
                == fields.Datetime.to_datetime(calendar_event.start)
                and r.partner_id == calendar_event.target_partner_id
                and r.user_id == calendar_event.user_id
            )
            if event_planner:
                if event_planner.calendar_summary_id != self:
                    event_planner.calendar_summary_id = self
                    event_planner.off_planning = True
            else:
                calendar_event.with_context(
                    default_calendar_summary_id=self.id,
                    default_date=calendar_event.start,
                )._create_event_planner()
        # Search sale orders off planning
        date_from = self._get_datetime_from_date_tz_hour(
            self.date, self.env.company.sale_planner_order_cut_hour
        )
        date_to = date_from + timedelta(days=1)
        sales = self.env["sale.order"].search(
            [
                ("user_id", "=", self.user_id.id),
                ("date_order", ">=", date_from),
                ("date_order", "<", date_to),
                ("sale_planner_calendar_event_id", "=", False),
            ]
        )
        sales.action_set_planner_calendar_event()

    @api.model
    def _get_datetime_from_date_tz_hour(self, date, hour_float):
        """
        Compute date in UTC format
        :return: Datetime in UTC format
        """
        hour_str = str(timedelta(hours=hour_float)).zfill(8)
        date_str = "{} {}".format(fields.Date.to_string(date), hour_str)
        date_time = fields.Datetime.to_datetime(date_str)
        user_tz = pytz.timezone(self.env.user.tz)
        utc_tz = pytz.timezone("UTC")
        time_utc = user_tz.localize(date_time).astimezone(utc_tz).replace(tzinfo=None)
        return time_utc

    def action_event_planner(self):
        if not self.sale_planner_calendar_event_ids:
            self.action_process()
        action = self.env.ref(
            "sale_planner_calendar.action_sale_planner_calendar_event"
        )
        action = action.read()[0]
        action["domain"] = [("id", "in", self.sale_planner_calendar_event_ids.ids)]
        action["context"] = {
            "default_off_planning": True,
            "default_calendar_summary_id": self.id,
            "search_default_state_pending": 1,
        }
        action["views"] = [
            (
                self.env.ref(
                    "sale_planner_calendar.view_sale_planner_calendar_kanban"
                ).id,
                "kanban",
            ),
            (
                self.env.ref(
                    "sale_planner_calendar.view_sale_planner_calendar_form"
                ).id,
                "form",
            ),
            (
                self.env.ref(
                    "sale_planner_calendar.view_sale_planner_calendar_tree"
                ).id,
                "tree",
            ),
        ]
        action["view_mode"] = "kanban,form,tree"
        return action

    def action_open_payment_sheet(self):
        """
        Open payments sheets related to any event
        """
        payment_sheets = self.sale_planner_calendar_event_ids.mapped(
            "payment_sheet_line_ids.sheet_id"
        )
        action = self.env.ref("sale_payment_sheet.action_sale_payment_sheet")
        action = action.read()[0]
        if len(payment_sheets) > 1:
            action["domain"] = [("id", "in", payment_sheets.ids)]
        else:
            action["views"] = [
                (
                    self.env.ref("sale_payment_sheet.view_sale_payment_sheet_form").id,
                    "form",
                )
            ]
            action["res_id"] = payment_sheets.id
        return action

    def action_open_issue(self):
        """
        Open issues related to any event
        """
        issues = self.sale_planner_calendar_event_ids.filtered("calendar_issue_type_id")
        action = self.env.ref(
            "sale_planner_calendar.action_sale_planner_calendar_issue_tree"
        )
        action = action.read()[0]
        action["domain"] = [("id", "in", issues.ids)]
        return action

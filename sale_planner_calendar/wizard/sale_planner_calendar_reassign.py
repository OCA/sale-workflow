# Copyright 2021 Tecnativa - Sergio Teruel
# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class SalePlannerCalendarReassignWiz(models.TransientModel):
    _name = "sale.planner.calendar.reassign.wiz"
    _description = "Sale planner calendar reassign wizard"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
        domain="[('share','=',False)]",
    )
    event_type_id = fields.Many2one(
        comodel_name="calendar.event.type", string="Event type"
    )
    week_list = fields.Selection(
        [
            ("mon", "Monday"),
            ("tue", "Tuesday"),
            ("wed", "Wednesday"),
            ("thu", "Thursday"),
            ("fri", "Friday"),
            ("sat", "Saturday"),
            ("sun", "Sunday"),
        ],
        string="Weekday",
    )
    partner_id = fields.Many2one(comodel_name="res.partner")
    partner_user_id = fields.Many2one(
        comodel_name="res.users",
        domain="[('share','=',False)]",
    )
    new_user_id = fields.Many2one(
        comodel_name="res.users",
        string="New salesperson",
        domain="[('share','=',False)]",
    )
    new_start = fields.Date()
    new_end = fields.Date()
    assign_new_salesperson_to_partner = fields.Boolean()
    unsuscribe_old_salesperson = fields.Boolean()
    line_ids = fields.One2many(
        comodel_name="sale.planner.calendar.reassign.line.wiz",
        inverse_name="reassign_wiz_id",
    )

    @api.onchange(
        "user_id", "event_type_id", "week_list", "partner_user_id", "partner_id"
    )
    def onchange_filter_values(self):
        self.line_ids = False

    def action_get_lines(self):
        domain = [
            ("recurrency", "=", True),
            ("recurrence_id.until", ">", self.new_start or fields.Date.today()),
            ("is_base_recurrent_event", "=", True),
            ("target_partner_id", "!=", False),
        ]
        if self.user_id:
            domain.append(("user_id", "=", self.user_id.id))
        if self.partner_user_id:
            domain.append(("target_partner_id.user_id", "=", self.partner_user_id.id))
        if self.partner_id:
            domain.append(("target_partner_id", "=", self.partner_id.id))
        if self.event_type_id:
            domain.append(("categ_ids", "in", self.event_type_id.ids))
        if self.week_list:
            domain.append((self.week_list, "=", True))
        calendar_events = self.env["calendar.event"].search(domain)
        self.line_ids = False
        for calendar_event in calendar_events:
            self.env["sale.planner.calendar.reassign.line.wiz"].create(
                {
                    "reassign_wiz_id": self.id,
                    "calendar_event_id": calendar_event.id,
                    # "event_categ_ids": [(6, 0, calendar_event.categ_ids.ids)],
                    "event_user_id": calendar_event.user_id.id,
                    "partner_id": calendar_event.target_partner_id.id,
                    "event_start": calendar_event.start,
                    "until": calendar_event.until,
                }
            )

    def action_assign_new_salesperson(self):
        lines = self.line_ids.filtered("selected")
        lines.new_user_id = self.new_user_id
        lines.selected = False
        self.new_user_id = False

    def select_all_lines(self):
        self.line_ids.selected = True

    def unselect_all_lines(self):
        self.line_ids.selected = False

    def apply(self):
        # Not send emails to attendees in copy methods
        if not self.env.company.sale_planner_mail_to_attendees:
            self = self.with_context(no_mail_to_attendees=True, dont_notify=True)
        for line in self.line_ids:
            if not line.new_user_id:
                continue
            if self.assign_new_salesperson_to_partner:
                line.partner_id.with_context(
                    skip_sale_planner_check=True
                ).user_id = line.new_user_id
            # If new_start is empty only update partner user_id
            if not self.new_start:
                continue
            old_event = line.calendar_event_id
            recurrence_events = old_event.recurrence_id.calendar_event_ids
            if self.new_end:
                new_base_event_end = recurrence_events.filtered(
                    lambda ce: ce.start.date() >= self.new_end
                ).sorted("start")[:1]
                partner_ids = (
                    new_base_event_end.partner_ids
                    + line.event_user_id.partner_id
                    - line.new_user_id.partner_id
                ).ids
                new_base_event_end.write(
                    {
                        "recurrence_update": "future_events",
                        "user_id": line.event_user_id.id,
                        "partner_ids": [
                            (6, False, partner_ids),
                        ],
                        "is_dynamic_end_date": old_event.is_dynamic_end_date,
                    }
                )
            new_base_event_start = recurrence_events.filtered(
                lambda ce: ce.start.date() >= self.new_start
            ).sorted("start")[:1]
            partner_ids = (
                new_base_event_start.partner_ids
                - line.event_user_id.partner_id
                + line.new_user_id.partner_id
            ).ids
            new_base_event_start.write(
                {
                    "recurrence_update": "future_events",
                    "user_id": line.new_user_id.id,
                    "partner_ids": [
                        (6, False, partner_ids),
                    ],
                    # Next fields has different behavior if 'self.new_end' field has a
                    # value
                    "is_dynamic_end_date": False
                    if self.new_end
                    else old_event.is_dynamic_end_date,
                    "unsubscribe_date": self.new_end,
                }
            )

            old_event_vals = {
                "recurrence_update": "all_events",
                "is_dynamic_end_date": False,
            }
            if self.unsuscribe_old_salesperson and not self.new_end:
                old_event_vals["unsubscribe_date"] = self.new_start
            old_event.write(old_event_vals)
            line.update_subscriptions()
        self.action_get_lines()

    @api.model
    def _unsubscribe(self, partner, user):
        if partner.user_id != user:
            partner.message_unsubscribe(partner_ids=user.partner_id.ids)
        unsubscribe_domain = [
            ("message_partner_ids", "in", partner.ids),
            ("user_id", "!=", user.id),
            "|",
            ("partner_id", "=", partner.id),
            ("partner_shipping_id", "=", partner.id),
        ]
        self.env["sale.order"].search(unsubscribe_domain).message_unsubscribe(
            partner_ids=user.partner_id.ids
        )
        self.env["account.move"].search(unsubscribe_domain).message_unsubscribe(
            partner_ids=user.partner_id.ids
        )

    @api.model
    def cron_unsubscribe(self, date=None):
        if date is None:
            date = fields.Date.today()
        events = self.env["calendar.event"].search(
            [
                ("unsubscribe_date", "<=", date),
            ]
        )
        for event in events:
            self._unsubscribe(event.target_partner_id, event.user_id)
        events.unsubscribe_date = False


class SalePlannerCalendarReassignLineWiz(models.TransientModel):
    _name = "sale.planner.calendar.reassign.line.wiz"
    _description = "Sale planner calendar reassign lines wizard"

    reassign_wiz_id = fields.Many2one(comodel_name="sale.planner.calendar.reassign.wiz")
    selected = fields.Boolean()
    calendar_event_id = fields.Many2one(comodel_name="calendar.event", readonly=True)
    event_categ_ids = fields.Many2many(
        comodel_name="calendar.event.type", related="calendar_event_id.categ_ids"
    )
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=True)
    partner_user_id = fields.Many2one(
        string="Partner salesperson",
        comodel_name="res.users",
        related="partner_id.user_id",
    )
    event_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Planned user",
        readonly=True,
        domain="[('share','=',False)]",
    )
    new_user_id = fields.Many2one(
        comodel_name="res.users",
        domain="[('share','=',False)]",
    )
    event_start = fields.Datetime(readonly=True)
    until = fields.Datetime(readonly=True)

    def update_subscriptions(self):
        for line in self:
            backward_date = fields.Date.today() - timedelta(
                days=self.env.company.susbscriptions_backward_days
            )
            sale_orders = self.env["sale.order"].search(
                [
                    ("date_order", ">=", backward_date),
                    ("partner_id", "=", line.partner_id.id),
                    ("user_id", "!=", line.new_user_id.id),
                ]
            )
            invoices = (
                self.env["account.move"]
                .sudo()
                .search(
                    [
                        ("move_type", "in", ["out_invoice", "out_refund"]),
                        ("user_id", "!=", line.new_user_id.id),
                        "|",
                        ("invoice_date", ">=", backward_date),
                        ("payment_state", "!=", "paid"),
                        "|",
                        ("partner_id", "=", line.partner_id.id),
                        ("partner_shipping_id", "=", line.partner_id.id),
                    ]
                )
            )
            for records in [line.partner_id, sale_orders, invoices]:
                records.message_subscribe(partner_ids=line.new_user_id.partner_id.ids)
        self.reassign_wiz_id.cron_unsubscribe()

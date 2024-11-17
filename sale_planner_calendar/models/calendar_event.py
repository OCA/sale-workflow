# Copyright 2021-2024 Tecnativa - Sergio Teruel
# Copyright 2021-2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re
from datetime import timedelta

import pytz
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    target_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Sale planner partner",
        help="Is the partner used in planner",
    )
    hour = fields.Float(compute="_compute_hour", inverse="_inverse_hour")
    target_partner_mobile = fields.Char(related="target_partner_id.mobile")
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
    sale_planner_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="target_partner_id.currency_id",
    )
    sale_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="sale_planner_calendar_event_id",
    )
    sale_planner_state = fields.Selection(
        [
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="pending",
        readonly=True,
        tracking=True,
    )
    calendar_issue_type_id = fields.Many2one(
        comodel_name="sale.planner.calendar.issue.type", ondelete="restrict"
    )
    comment = fields.Text()
    sale_order_subtotal = fields.Monetary(
        compute="_compute_sale_order_subtotal",
        currency_field="sale_planner_currency_id",
    )
    calendar_summary_id = fields.Many2one(
        comodel_name="sale.planner.calendar.summary",
        copy=False,
    )
    invoice_amount_residual = fields.Monetary(
        string="Invoice amount due",
        compute="_compute_invoice_amount_residual",
        compute_sudo=True,
        currency_field="sale_planner_currency_id",
    )
    off_planning = fields.Boolean(copy=False)
    payment_sheet_line_ids = fields.One2many(
        comodel_name="sale.payment.sheet.line",
        inverse_name="sale_planner_calendar_event_id",
    )
    # Helper fields for kanban views
    partner_ref = fields.Char(related="target_partner_id.ref")
    partner_name = fields.Char(compute="_compute_partner_name")
    partner_commercial_name = fields.Char(
        string="Commercial partner name",
        related="target_partner_id.commercial_partner_id.name",
    )
    partner_street = fields.Char(related="target_partner_id.street")
    partner_mobile = fields.Char(compute="_compute_contact")
    partner_contact_name = fields.Char(compute="_compute_contact")
    partner_city = fields.Char(related="target_partner_id.city")
    partner_user_id = fields.Many2one(
        related="target_partner_id.user_id", string="Partner salesperson"
    )
    sanitized_partner_mobile = fields.Char(compute="_compute_sanitized_partner_mobile")
    location_url = fields.Char(compute="_compute_location_url")
    categ_icons = fields.Char(compute="_compute_categ_icons")

    @api.depends("recurrence_id", "recurrence_id.calendar_event_ids")
    def _compute_is_base_recurrent_event(self):
        for record in self:
            record.is_base_recurrent_event = (
                record == record.recurrence_id.calendar_event_ids.sorted("start")[:1]
            )

    @api.depends("start")
    def _compute_hour(self):
        for rec in self:
            date = rec._get_hour_tz_offset()
            rec.hour = date.hour + date.minute / 60

    @api.depends("sale_ids.amount_untaxed")
    def _compute_sale_order_subtotal(self):
        for rec in self:
            rec.sale_order_subtotal = sum(rec.mapped("sale_ids.amount_untaxed"))

    @api.depends("target_partner_id")
    def _compute_invoice_amount_residual(self):
        partner_ids = self.mapped("target_partner_id.commercial_partner_id").ids
        groups = self.env["account.move"]._read_group(
            domain=[
                ("state", "=", "posted"),
                ("payment_state", "!=", "paid"),
                ("partner_id", "in", partner_ids),
            ],
            fields=["amount_residual_signed"],
            groupby=["partner_id"],
        )
        invoice_dic = {g["partner_id"][0]: g["amount_residual_signed"] for g in groups}
        for rec in self:
            amount_residual = invoice_dic.get(
                rec.target_partner_id.commercial_partner_id.id, 0.0
            )
            payment_amount = sum(
                rec.payment_sheet_line_ids.filtered(
                    lambda p: p.sheet_id.state == "open"
                ).mapped("amount")
            )
            rec.invoice_amount_residual = amount_residual - payment_amount

    @api.depends("target_partner_id")
    def _compute_partner_name(self):
        field_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_planner_calendar.partner_name_field",
                default="name",
            )
        )
        for event in self:
            # If more flexibility is needed use event.mapped(field_name)[0]
            event.partner_name = (
                event.target_partner_id[field_name]
                or event.target_partner_id.name
                or event.target_partner_id.commercial_partner_id.name
            )

    @api.depends("target_partner_id")
    def _compute_contact(self):
        for rec in self:
            contact = rec.target_partner_id.child_ids.filtered(
                "is_sale_planner_contact"
            )[:1]
            rec.partner_mobile = (contact.mobile or contact.phone) or (
                rec.target_partner_id.mobile or rec.target_partner_id.phone
            )
            rec.partner_contact_name = contact.name

    @api.depends("partner_mobile")
    def _compute_sanitized_partner_mobile(self):
        self.sanitized_partner_mobile = False
        for rec in self.filtered("partner_mobile"):
            rec.sanitized_partner_mobile = re.sub(r"\W+", "", rec.partner_mobile)

    @api.depends("target_partner_id")
    def _compute_location_url(self):
        # The url is built to access the location from a google link. This will be done
        # taking into account the location of the calendar event associated with the calendar
        # planner event. If this location is not defined, the client's coordinates will
        # be taken into account if they are defined, otherwise the client's address
        # will be taken into account.
        self.location_url = False
        for event in self:
            event_location = event.location
            partner_latitude = str(event.target_partner_id.partner_latitude).replace(
                ",", "."
            )
            partner_longitude = str(event.target_partner_id.partner_longitude).replace(
                ",", "."
            )
            partner_location = f"{event.partner_city}+{event.partner_street}"
            if event_location:
                event.location_url = event_location.replace(" ", "+")
            elif partner_latitude != "0.0" or partner_longitude != "0.0":
                event.location_url = f"{partner_latitude}%2C{partner_longitude}"
            elif partner_location:
                event.location_url = partner_location.replace(" ", "+")

    @api.depends("categ_ids")
    def _compute_categ_icons(self):
        for event in self:
            categ_icons_list = []
            for categ in event.categ_ids.filtered("icon"):
                # Avoid repeat same icon
                if categ.icon not in categ_icons_list:
                    categ_icons_list.append(categ.icon)
            event.categ_icons = ",".join(categ_icons_list)

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

    @api.onchange("categ_ids")
    def _onchange_categ_ids(self):
        if not self.name and self.categ_ids:
            self.name = self.categ_ids[:1].name
        # Clean name if is equal to stored categ name and this categ is removed
        elif not self.categ_ids and self.name == self._origin.categ_ids[:1].name:
            self.name = False

    def action_open_sale_order(self, new_order=False):
        """
        Search or Create an event planner  linked to sale order
        """
        action_xml_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_planner_calendar.action_open_sale_order",
                "sale.action_quotations_with_onboarding",
            )
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(action_xml_id)
        if new_order:
            action["name"] = "New Quotation"
            action["context"] = self.env.context
            return action
        # Create sale order to planner partner or commercial partner depending of the
        # system parameter
        create_so_to_commercial_partner = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_planner_calendar.create_so_to_commercial_partner", "False")
        )
        partner = (
            self.target_partner_id
            if create_so_to_commercial_partner == "False"
            else self.target_partner_id.commercial_partner_id
        )
        action["context"] = {
            "default_sale_planner_calendar_event_id": self.id,
            "default_partner_id": partner.id,
            "default_partner_shipping_id": self.target_partner_id.id,
            "default_user_id": self.user_id.id,
        }
        if len(self.sale_ids) > 1:
            action["domain"] = [("sale_planner_calendar_event_id", "=", self.id)]
        else:
            action["views"] = list(filter(lambda v: v[1] == "form", action["views"]))
            action["res_id"] = self.sale_ids.id
        return action

    def action_open_invoices(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_payment_sheet.action_invoice_sale_payment_sheet"
        )
        ctx = safe_eval(action["context"])
        ctx.update(
            {
                "default_partner_id": self.target_partner_id.id,
            }
        )
        action["context"] = ctx
        domain = safe_eval(action["domain"])
        domain.append(
            ("partner_id", "=", self.target_partner_id.commercial_partner_id.id),
        )
        action["domain"] = domain
        return action

    def action_open_unpaid_invoice(self):
        domain = [
            ("state", "=", "posted"),
            ("move_type", "in", ["out_invoice", "out_refund"]),
            ("partner_id", "=", self.target_partner_id.commercial_partner_id.id),
            ("payment_state", "!=", "paid"),
        ]
        unpaid_invoices = self.env["account.move"].search(domain)
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_payment_sheet.action_sale_invoice_payment_wiz"
        )
        ctx = safe_eval(action["context"])
        ctx.update(
            {
                "invoice_ids": unpaid_invoices.ids,
                "default_sale_planner_calendar_event_id": self.id,
                "default_partner_id": self.target_partner_id.id,
            }
        )
        action["context"] = ctx
        return action

    def action_done(self):
        self.write(
            {
                "sale_planner_state": "done",
            }
        )

    def action_cancel(self):
        self.write(
            {
                "sale_planner_state": "cancel",
                "comment": "Not done",
            }
        )

    def action_pending(self):
        self.write(
            {
                "sale_planner_state": "pending",
                "comment": False,
            }
        )

    def action_open_issue(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_planner_calendar.action_sale_planner_calendar_issue"
        )
        action["res_id"] = self.id
        return action

    def action_apply_issue(self):
        pass

    def _get_hour_tz_offset(self):
        timezone = self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        self_tz = self.with_context(tz=timezone)
        date = fields.Datetime.context_timestamp(self_tz, self.start)
        return date

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

    @api.model
    def cron_update_dynamic_final_date(self):
        events_to_update = self.search(
            [("is_dynamic_end_date", "=", True), ("is_base_recurrent_event", "=", True)]
        )
        new_date = fields.Date.today() + relativedelta(
            months=self.env.company.sale_planner_forward_months, day=31
        )
        events_to_update.until = new_date

# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class SalePlannerCalendarEvent(models.Model):
    _name = "sale.planner.calendar.event"
    _description = "Sale planner calendar event"

    name = fields.Char(string="Subject")
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company.id
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="partner_id.currency_id",
    )
    date = fields.Datetime(default=fields.Datetime.now)
    calendar_event_id = fields.Many2one(
        comodel_name="calendar.event",
    )
    calendar_event_date = fields.Datetime(index=True)
    user_id = fields.Many2one(
        comodel_name="res.users",
        default=lambda self: self.env.user.id,
        index=True,
        domain="[('share','=',False)]",
    )
    partner_id = fields.Many2one(comodel_name="res.partner", index=True)
    sale_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="sale_planner_calendar_event_id",
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="pending",
        readonly=True,
    )
    calendar_issue_type_id = fields.Many2one(
        comodel_name="sale.planner.calendar.issue.type", ondelete="restrict"
    )
    calendar_event_profile_id = fields.Many2one(
        comodel_name="sale.planner.calendar.event.profile"
    )
    comment = fields.Text()
    sale_order_subtotal = fields.Monetary(
        compute="_compute_sale_order_subtotal", currency_field="currency_id"
    )
    calendar_summary_id = fields.Many2one(
        comodel_name="sale.planner.calendar.summary",
    )
    invoice_amount_residual = fields.Monetary(
        string="Invoice amount due",
        compute="_compute_invoice_amount_residual",
        compute_sudo=True,
    )
    off_planning = fields.Boolean()
    payment_sheet_line_ids = fields.One2many(
        comodel_name="sale.payment.sheet.line",
        inverse_name="sale_planner_calendar_event_id",
    )
    # Helper fields to kanban views
    partner_ref = fields.Char(related="partner_id.ref")
    partner_name = fields.Char(compute="_compute_partner_name")
    partner_commercial_name = fields.Char(
        string="Commercial partner name",
        related="partner_id.commercial_partner_id.name",
    )
    partner_street = fields.Char(related="partner_id.street")
    partner_mobile = fields.Char(compute="_compute_contact")
    partner_contact_name = fields.Char(compute="_compute_contact")
    partner_city = fields.Char(related="partner_id.city")
    sanitized_partner_mobile = fields.Char(compute="_compute_sanitized_partner_mobile")
    location_url = fields.Char(compute="_compute_location_url")
    profile_icon = fields.Char(related="calendar_event_profile_id.icon")

    @api.depends("sale_ids.amount_untaxed")
    def _compute_sale_order_subtotal(self):
        for rec in self:
            rec.sale_order_subtotal = sum(rec.mapped("sale_ids.amount_untaxed"))

    # @api.depends("target_partner_id")
    def _compute_invoice_amount_residual(self):
        groups = self.env["account.move"].read_group(
            [
                ("state", "=", "posted"),
                ("payment_state", "!=", "paid"),
                (
                    "partner_id",
                    "in",
                    self.mapped("partner_id.commercial_partner_id").ids,
                ),
            ],
            ["amount_residual_signed"],
            ["partner_id"],
        )
        invoice_dic = {g["partner_id"][0]: g["amount_residual_signed"] for g in groups}
        for rec in self:
            amount_residual = invoice_dic.get(
                rec.partner_id.commercial_partner_id.id, 0.0
            )
            rec.invoice_amount_residual = amount_residual - sum(
                rec.payment_sheet_line_ids.filtered(
                    lambda p: p.sheet_id.state == "open"
                ).mapped("amount")
            )

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
                event.partner_id[field_name]
                or event.partner_id.name
                or event.partner_id.commercial_partner_id.name
            )

    def _compute_contact(self):
        for rec in self:
            contact = rec.partner_id.child_ids.filtered("is_sale_planner_contact")[:1]
            rec.partner_mobile = (contact.mobile or contact.phone) or (
                rec.partner_id.mobile or rec.partner_id.phone
            )
            rec.partner_contact_name = contact.name

    def _compute_sanitized_partner_mobile(self):
        self.sanitized_partner_mobile = False
        for rec in self.filtered("partner_mobile"):
            rec.sanitized_partner_mobile = re.sub(r"\W+", "", rec.partner_mobile)

    def _compute_location_url(self):
        # The url is built to access the location from a google link. This will be done
        # taking into account the location of the calendar event associated with the calendar
        # planner event. If this location is not defined, the client's coordinates will
        # be taken into account if they are defined, otherwise the client's address
        # will be taken into account.
        self.location_url = False
        for rec in self:
            event_location = rec.calendar_event_id.location
            partner_latitude = str(rec.partner_id.partner_latitude).replace(",", ".")
            partner_longitude = str(rec.partner_id.partner_longitude).replace(",", ".")
            partner_location = f"{rec.partner_city}+{rec.partner_street}"
            if event_location:
                self.location_url = event_location.replace(" ", "+")
            elif partner_latitude != "0.0" or partner_longitude != "0.0":
                self.location_url = f"{partner_latitude}%2C{partner_longitude}"
            elif partner_location:
                self.location_url = partner_location.replace(" ", "+")

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
            self.partner_id
            if create_so_to_commercial_partner == "False"
            else self.partner_id.commercial_partner_id
        )
        action["context"] = {
            "default_sale_planner_calendar_event_id": self.id,
            "default_partner_id": partner.id,
            "default_partner_shipping_id": self.partner_id.id,
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
                "default_partner_id": self.partner_id.id,
            }
        )
        action["context"] = ctx
        domain = safe_eval(action["domain"])
        domain.append(
            ("partner_id", "=", self.partner_id.commercial_partner_id.id),
        )
        action["domain"] = domain
        return action

    def action_open_unpaid_invoice(self):
        domain = [
            ("state", "=", "posted"),
            ("move_type", "in", ["out_invoice", "out_refund"]),
            ("partner_id", "=", self.partner_id.commercial_partner_id.id),
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
                "default_partner_id": self.partner_id.id,
            }
        )
        action["context"] = ctx
        return action

    def action_done(self):
        self.write(
            {
                "state": "done",
                "date": fields.Datetime.now(),
                # "comment": 'Done',
            }
        )

    def action_cancel(self):
        self.write(
            {
                "state": "cancel",
                "comment": "Not done",
                "date": fields.Datetime.now(),
            }
        )

    def action_pending(self):
        self.write(
            {
                "state": "pending",
                "comment": False,
                "date": self.calendar_event_date,
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

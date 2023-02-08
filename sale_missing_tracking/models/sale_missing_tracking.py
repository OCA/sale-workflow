# Copyright 2021 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleMissingTrackingReason(models.Model):
    _name = "sale.missing.tracking.reason"
    _description = "Sale Missing Cart Tracking Reason"

    name = fields.Char(required=True)
    note = fields.Text()


class SaleMissingTracking(models.Model):
    _name = "sale.missing.tracking"
    _inherit = ["mail.thread"]
    _description = "Sale Missing Cart Tracking"
    _order = "partner_id, date_order desc, id desc"

    active = fields.Boolean(default=True)
    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
        required=True,
        ondelete="cascade",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("request", "Requested"),
            ("approved", "Approved"),
            ("refused", "Refused"),
            ("recovered", "Recovered"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
    )
    company_id = fields.Many2one(
        comodel_name="res.company", related="order_id.company_id", store=True
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency", related="order_id.currency_id", store=True
    )
    date_order = fields.Datetime(related="order_id.date_order", store=True, index=True)
    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.partner_id.commercial_partner_id",
        store=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.partner_id",
        store=True,
        index=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users", related="order_id.user_id", store=True
    )
    team_id = fields.Many2one(
        comodel_name="crm.team", related="order_id.team_id", store=True
    )
    product_id = fields.Many2one(comodel_name="product.product", index=True)
    last_sale_line_id = fields.Many2one(comodel_name="sale.order.line")
    reason_id = fields.Many2one(comodel_name="sale.missing.tracking.reason", index=True)
    reason_note = fields.Text(
        compute="_compute_reason_note", store=True, readonly=False
    )
    consumption = fields.Monetary()
    tracking_exception_ids = fields.Many2many(
        comodel_name="sale.missing.tracking.exception",
        relation="missing_tracking_exception_missing_tracking_rel",
        column1="tracking_id",
        column2="exception_id",
        string="Missing sales tracking exceptions",
    )

    def action_open_sale_order(self):
        """
        Action to open sale order related
        """
        self.ensure_one()
        return self.order_id.get_formview_action()

    @api.depends("reason_id")
    def _compute_reason_note(self):
        for rec in self:
            rec.reason_note = rec.reason_id.note

    def name_get(self):
        return [
            (x.id, f"{x.partner_id.name} - {x.product_id.display_name}") for x in self
        ]

    @api.model
    def missing_tracking_notification(self):
        now = fields.Datetime.now()
        date_from = now - relativedelta(
            months=self.env.company.sale_missing_months_consumption
        )
        date_to = now - relativedelta(
            days=self.env.company.sale_missing_days_notification
        )
        domain = [
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("state", "in", ["draft", "request", "refused"]),
        ]
        missing_groups = self.read_group(
            domain=domain,
            fields=["team_id", "partner_id", "product_id"],
            groupby=["team_id", "partner_id", "product_id"],
            lazy=False,
        )
        exception_groups = self.env["sale.missing.tracking.exception"].read_group(
            domain=[("state", "=", "approved")],
            fields=["partner_id", "product_id"],
            groupby=["partner_id", "product_id"],
            lazy=False,
        )
        exception_set = {
            (g["partner_id"][0], g["product_id"][0]) for g in exception_groups
        }
        missing_dic = defaultdict(set)
        for group in missing_groups:
            missing_dic[group["team_id"][0]].append(
                (group["partner_id"][0], group["product_id"][0])
            )
        for team_id, missing_set in missing_dic.items():
            result_set = missing_set - exception_set
            if result_set:
                self.send_notification(team_id)

    @api.model
    def send_notification(self, team_id):
        template = self.env.ref(
            "sale_missing_tracking.missing_tracking_notification_template"
        )
        mt = self.env.ref("sale_missing_tracking.mt_sale_missing_tracking_notification")
        team = self.env["crm.team"].browse(team_id)
        recipients = team.message_follower_ids.filtered(
            lambda f: mt in f.subtype_ids
        ).mapped("partner_id")
        composer = (
            self.env["mail.compose.message"]
            .with_context(
                lang=self.env.user.lang,
                default_composition_mode="mass_mail",
                default_notify=True,
                default_model=self._name,
                default_template_id=template.id,
                active_ids=self.ids,
                default_partner_ids=recipients.ids,
            )
            .create({})
        )
        values = composer.onchange_template_id(
            template.id, "mass_mail", self._name, self.id
        )["value"]
        composer.write(values)
        composer.send_mail()
        return True

    def action_create_exception(self):
        exception_dic = {}
        for rec in self:
            key = (rec.partner_id.id, rec.product_id.id)
            if key not in exception_dic:
                exception_dic[key] = {
                    "partner_id": rec.partner_id.id,
                    "product_id": rec.product_id.id,
                    "user_id": rec.user_id.id,
                    "reason_id": rec.reason_id.id,
                    "reason_note": rec.reason_note,
                    "consumption": rec.consumption,
                }
        exceptions = self.env["sale.missing.tracking.exception"].create(
            exception_dic.values()
        )
        if self.env.user.has_group(
            "sale_missing_tracking.group_sale_missing_tracking_manager"
        ):
            exceptions.action_approve()
        else:
            exceptions.action_request()
        # Set exceptions to trackings
        for rec in self:
            rec.tracking_exception_ids = exceptions.filtered(
                lambda e: e.partner_id == rec.partner_id
                and e.product_id == rec.product_id
            )
        return exceptions

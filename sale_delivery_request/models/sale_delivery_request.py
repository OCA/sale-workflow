from datetime import datetime, timedelta

from markupsafe import Markup
from pytz import UTC

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import html_escape


class SaleDeliveryRequest(models.Model):
    _name = "sale.delivery.request"
    _description = "Delivery Date Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, request_datetime desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sales Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    partner_id = fields.Many2one(
        related="sale_order_id.partner_id",
        store=True,
        index=True,
    )
    sale_order_state = fields.Selection(
        related="sale_order_id.state",
        store=True,
        string="Sale Order Status",
    )
    company_id = fields.Many2one(
        related="sale_order_id.company_id",
        store=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("expired", "Expired"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    is_priority_request = fields.Boolean(
        string="Priority",
        default=False,
        tracking=True,
    )
    priority = fields.Selection(
        [
            ("0", "Normal"),
            ("1", "Favorite"),
        ],
        default="0",
        string="Favorite",
        compute="_compute_priority",
        store=True,
        readonly=False,
    )
    request_datetime = fields.Datetime(
        string="Request Date",
        default=fields.Datetime.now,
        required=True,
        readonly=True,
        copy=False,
    )
    response_datetime = fields.Datetime(
        string="Response Date",
        tracking=True,
        readonly=True,
        copy=False,
    )
    expiration_date = fields.Date(
        compute="_compute_expiration_date",
        store=True,
    )
    response_delay_hours = fields.Float(
        string="Response Delay",
        compute="_compute_response_delay_hours",
        store=True,
        group_operator="avg",
    )
    line_ids = fields.One2many(
        comodel_name="sale.delivery.request.line",
        inverse_name="delivery_request_id",
        string="Request Lines",
    )
    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="sale_delivery_request_user_rel",
        string="Responsibles",
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "sale.delivery.request"
                ) or _("New")
        records = super().create(vals_list)
        records._notify_responsible()
        return records

    def write(self, vals):
        if (
            not self.env.user.has_group(
                "sale_delivery_request.group_sale_delivery_request_manager"
            )
            and not self.env.su
        ):
            allowed = {"user_ids"}
            forbidden = set(vals.keys()) - allowed
            if forbidden:
                raise UserError(
                    _(
                        "You are not allowed to modify the following fields: %s",
                        ", ".join(sorted(forbidden)),
                    )
                )
        if "user_ids" in vals:
            old_users = {rec.id: rec.user_ids for rec in self}
            res = super().write(vals)
            for rec in self:
                new_users = rec.user_ids - old_users.get(rec.id, self.env["res.users"])
                if new_users:
                    rec._notify_new_responsible(new_users)
        else:
            res = super().write(vals)
        return res

    def _notify_responsible(self):
        """
        Add all responsibles as followers and send a notification.
        Called from create() to notify all assigned users.
        """
        for rec in self:
            if not rec.user_ids:
                continue
            rec._notify_new_responsible(rec.user_ids)

    def _notify_new_responsible(self, users):
        """
        Add the given users as followers and send them a notification.
        Called from write() with only newly added users to avoid
        re-notifying existing responsibles.
        """
        self.ensure_one()
        partners = users.mapped("partner_id")
        new_partners = partners - self.message_partner_ids
        if new_partners:
            self.message_subscribe(partner_ids=new_partners.ids)
        self.message_post(
            body=_(
                "You have been assigned as responsible " "for this delivery request."
            ),
            partner_ids=partners.ids,
            message_type="notification",
            subtype_xmlid="mail.mt_note",
        )

    @api.onchange("sale_order_id")
    def _onchange_sale_order_id(self):
        """
        Auto-populate request lines from the sale order.
        """
        if not self.sale_order_id:
            self.line_ids = [(5, 0, 0)]
            return
        lines = [(5, 0, 0)]
        for sol in self.sale_order_id.order_line.filtered(
            lambda x: not x.display_type and x.product_id.type in ("consu", "product")
        ):
            remaining = sol.product_uom_qty - sol.qty_delivered
            if remaining > 0:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "sale_order_line_id": sol.id,
                            "quantity": remaining,
                        },
                    )
                )
        self.line_ids = lines

    @api.depends("response_datetime")
    def _compute_expiration_date(self):
        for rec in self:
            if rec.response_datetime:
                days = rec.company_id.delivery_request_expiration_days
                rec.expiration_date = rec.response_datetime.date() + timedelta(
                    days=days
                )
            else:
                rec.expiration_date = False

    @api.depends("request_datetime", "response_datetime")
    def _compute_response_delay_hours(self):
        for rec in self:
            if rec.request_datetime and rec.response_datetime:
                delta = rec.response_datetime - rec.request_datetime
                rec.response_delay_hours = delta.total_seconds() / 3600.0
            else:
                rec.response_delay_hours = 0.0

    @api.depends("is_priority_request")
    def _compute_priority(self):
        for rec in self:
            if rec.is_priority_request:
                rec.priority = "1"

    def _get_calendar(self):
        """
        Return the company resource.calendar for business days computation.
        """
        self.ensure_one()
        return self.company_id.resource_calendar_id

    def _compute_business_days_between(self, dt_from, dt_to):
        """
        Compute the number of business days between two datetimes
        using the resource calendar (respecting leaves / public holidays).

        Returns an integer count of distinct working dates.
        """
        self.ensure_one()
        calendar = self._get_calendar()
        if not calendar:
            # Fallback: simple weekday count
            return self._simple_business_days(dt_from.date(), dt_to.date())
        if not dt_from.tzinfo:
            dt_from = dt_from.replace(tzinfo=UTC)
        if not dt_to.tzinfo:
            dt_to = dt_to.replace(tzinfo=UTC)
        intervals = calendar._work_intervals_batch(dt_from, dt_to, compute_leaves=True)[
            False
        ]
        working_dates = set()
        for start, _stop, _meta in intervals:
            working_dates.add(start.date())
        return len(working_dates)

    @staticmethod
    def _simple_business_days(date_from, date_to):
        """
        Fallback: count Mon-Fri days between two dates.
        """
        count = 0
        current = date_from
        while current <= date_to:
            if current.weekday() < 5:
                count += 1
            current += timedelta(days=1)
        return count

    def action_send_request(self):
        """
        Sales sends the request to Planning.
        """
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Cannot send a request without lines."))
            rec.state = "pending"

    def action_confirm(self):
        """
        Planning confirms all dates.

        Pre-confirmation requests (SO not yet confirmed): apply dates to SO
        lines and optionally auto-confirm the SO for priority requests.

        Post-confirmation requests (SO already confirmed): apply dates and
        reschedule stock moves via cancel+relaunch.
        """
        post_confirmation = self.filtered(lambda r: r.sale_order_id.state == "sale")
        pre_confirmation = self - post_confirmation

        for rec in pre_confirmation:
            if not rec.line_ids or not all(
                line.promised_date_absolute for line in rec.line_ids
            ):
                raise UserError(
                    _(
                        "All request lines must have a promised date "
                        "before confirming."
                    )
                )
            rec.response_datetime = fields.Datetime.now()
            rec._compute_lines_offset()
            rec.state = "confirmed"
            rec.sale_order_id._apply_delivery_request_dates(rec)
            rec._notify_sale_order_followers()
            if rec.is_priority_request:
                order = rec.sale_order_id
                if order.state in ("draft", "sent"):
                    order.action_confirm()

        for rec in post_confirmation:
            if not rec.line_ids or not all(
                line.promised_date_absolute for line in rec.line_ids
            ):
                raise UserError(
                    _(
                        "All request lines must have a promised date "
                        "before confirming."
                    )
                )
            rec.response_datetime = fields.Datetime.now()
            rec._compute_lines_offset()
            rec.state = "confirmed"
            rec.sale_order_id._apply_delivery_request_dates_stock(rec)
            rec.sale_order_id.message_post(
                body=_(
                    "Delivery request %s confirmed. "
                    "Commitment dates updated and stock pickings rescheduled.",
                    rec.name,
                ),
                message_type="notification",
                subtype_xmlid="mail.mt_comment",
            )

    def _notify_sale_order_followers(self):
        """
        Post a message on the related sale order to notify its followers
        that the delivery request has been confirmed and the SO can be confirmed.
        """
        for rec in self:
            order = rec.sale_order_id
            if not order:
                continue
            order.message_post(
                body=Markup(
                    "%(message)s "
                    "<a href='#' data-oe-model='sale.delivery.request' "
                    "data-oe-id='%(dr_id)s'>%(dr_name)s</a>. "
                    "%(footer)s"
                )
                % {
                    "message": _("Delivery request"),
                    "dr_id": rec.id,
                    "dr_name": html_escape(rec.name),
                    "footer": _(
                        "has been confirmed. Delivery dates have been set. "
                        "The sales order can now be confirmed."
                    ),
                },
                message_type="notification",
                subtype_xmlid="mail.mt_comment",
            )

    def action_set_expired(self):
        for rec in self:
            rec.state = "expired"

    def action_assign_date_all(self):
        """
        Open wizard / set a single date for all lines at once.
        """
        self.ensure_one()
        return {
            "name": _("Assign Date to All Lines"),
            "type": "ir.actions.act_window",
            "res_model": "sale.delivery.request.assign.date",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_delivery_request_id": self.id,
            },
        }

    def _compute_lines_offset(self):
        """
        Compute business_days_offset on each line based on
        request_datetime → promised_date_absolute.
        """
        self.ensure_one()
        request_dt = self.request_datetime
        for line in self.line_ids:
            if line.promised_date_absolute:
                promised_dt = datetime.combine(
                    line.promised_date_absolute,
                    datetime.max.time(),
                )
                offset = self._compute_business_days_between(request_dt, promised_dt)
                line.business_days_offset = offset

    def _create_priority_request(self):
        """
        Create a new priority delivery request from an expired one.
        """
        self.ensure_one()
        if self.state != "expired":
            raise UserError(
                _(
                    "Only expired delivery requests can be used to "
                    "create a new priority request."
                )
            )
        new_request = self.copy(
            {
                "state": "pending",
                "is_priority_request": True,
                "priority": "1",
            }
        )
        if not new_request.line_ids:
            for line in self.line_ids:
                line.copy({"delivery_request_id": new_request.id})
        return new_request

    @api.model
    def _cron_check_expiration(self):
        """
        Mark confirmed requests as expired if past expiration date.
        """
        today = fields.Date.context_today(self)
        expired_requests = self.search(
            [
                ("state", "=", "confirmed"),
                ("expiration_date", "<", today),
            ]
        )
        expired_requests.write({"state": "expired"})

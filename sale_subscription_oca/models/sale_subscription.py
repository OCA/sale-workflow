# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import datetime as dt
import logging
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError
from odoo.tools.misc import get_lang

logger = logging.getLogger(__name__)
ODOO_DATE_FORMAT = "%Y-%m-%d"


class SaleSubscription(models.Model):
    _name = "sale.subscription"
    _description = "Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    color = fields.Integer("Color Index")

    @staticmethod
    def string2datetime(string_date):
        return datetime.strptime(string_date, ODOO_DATE_FORMAT)

    def cron_subscription_management(self):
        today = date.today()
        query = []
        for subscription in self.search(query):
            if subscription.in_progress:
                if (
                    subscription.recurring_next_date == today
                    and subscription.sale_subscription_line_ids
                ):
                    try:
                        subscription.generate_invoice()
                        subscription._onchange_template_id()
                    except Exception:
                        logger.exception("Error during Subscriptions Management cron")
                if not subscription.recurring_rule_boundary:
                    if subscription.date == today:
                        subscription.action_close_subscription()

            else:
                if subscription.date_start == today:
                    subscription.action_start_subscription()
                    subscription.generate_invoice()
                    subscription._onchange_template_id()

    @api.depends("sale_subscription_line_ids")
    def _compute_total(self):
        for record in self:
            recurring_total = amount_tax = 0.0
            for order_line in record.sale_subscription_line_ids:
                recurring_total += order_line.price_subtotal
                amount_tax += order_line.amount_tax_line_amount
            record.update(
                {
                    "recurring_total": recurring_total,
                    "amount_tax": amount_tax,
                    "amount_total": recurring_total + amount_tax,
                }
            )

    def _compute_name(self):
        template_code = self.template_id.code if self.template_id.code else ""
        code = "{}".format(self.code) if self.code else ""
        slash = "/" if template_code and code else ""
        self.name = "{}{}{}".format(template_code, slash, code)

    @api.onchange("template_id", "date_start")
    def _onchange_template_id(self):
        self._compute_name()
        today = date.today()
        if self.date_start:
            today = self.date_start
        if self.template_id.recurring_rule_boundary == "unlimited":
            self.date = False
            self.recurring_rule_boundary = True
        else:
            self.date = (
                relativedelta(months=+self.template_id.recurring_rule_count)
                + self.date_start
            )
            self.recurring_rule_boundary = False
        self.terms = self.template_id.description
        if self.template_id and self.account_invoice_ids_count > 0:
            self.calculate_recurring_next_date(self.recurring_next_date)
        else:
            self.calculate_recurring_next_date(today)

    def calculate_recurring_next_date(self, start_date):
        if self.account_invoice_ids_count == 0:
            self.recurring_next_date = date.today()
        else:
            if self.template_id.recurring_rule_type == "days":
                self.recurring_next_date = start_date + dt.timedelta(
                    days=+int(self.template_id.recurring_interval)
                )
            elif self.template_id.recurring_rule_type == "weeks":
                self.recurring_next_date = start_date + dt.timedelta(
                    weeks=+int(self.template_id.recurring_interval)
                )
            elif self.template_id.recurring_rule_type == "months":
                self.recurring_next_date = start_date + relativedelta(
                    months=+int(self.template_id.recurring_interval)
                )
            elif self.template_id.recurring_rule_type == "years":
                self.recurring_next_date = start_date + relativedelta(
                    years=+int(self.template_id.recurring_interval)
                )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        self._compute_name()
        self.pricelist_id = self.partner_id.property_product_pricelist

    @api.onchange("code")
    def _onchange_code(self):
        self._compute_name()

    name = fields.Char(
        compute="_compute_name",
        store=True,
    )

    sequence = fields.Integer()
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner", required=True, string="Partner", index=True
    )

    fiscal_position_id = fields.Many2one(
        "account.fiscal.position",
        string="Fiscal Position",
        domain="[('company_id', '=', company_id)]",
        check_company=True,
    )

    active = fields.Boolean(default=True)

    template_id = fields.Many2one(
        comodel_name="sale.subscription.template",
        required=True,
        string="Subscription template",
    )

    code = fields.Char(
        string="Reference",
        default=lambda self: self.env["ir.sequence"].next_by_code("sale.subscription"),
    )

    in_progress = fields.Boolean(string="In progress", default=False)

    recurring_rule_boundary = fields.Boolean(string="Boundary", default=False)

    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist", required=True, string="Pricelist"
    )

    recurring_next_date = fields.Date(string="Next invoice date", default=date.today())

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Commercial agent",
        default=lambda self: self.env.user.id,
    )

    date_start = fields.Date(string="Start date", default=date.today())

    date = fields.Date(string="Finish date")

    description = fields.Text()

    sale_order_id = fields.Many2one(
        comodel_name="sale.order", string="Origin sale order"
    )

    terms = fields.Text(string="Terms and conditions")

    invoice_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="subscription_id",
        string="Invoices",
    )

    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="order_subscription_id",
        string="Orders",
    )

    recurring_total = fields.Monetary(
        compute="_compute_total", string="Recurring price", store=True
    )

    amount_tax = fields.Monetary(compute="_compute_total", store=True)

    amount_total = fields.Monetary(compute="_compute_total", store=True)

    tag_ids = fields.Many2many(comodel_name="sale.subscription.tag", string="Tags")

    image = fields.Binary("Image", related="user_id.image_512", store=True)

    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal")

    currency_id = fields.Many2one(
        related="pricelist_id.currency_id",
        depends=["pricelist_id"],
        store=True,
        ondelete="restrict",
    )

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = stages.search([], order=order)
        return stage_ids

    stage_id = fields.Many2one(
        comodel_name="sale.subscription.stage",
        string="Stage",
        tracking=True,
        group_expand="_read_group_stage_ids",
        store="true",
    )

    stage_str = fields.Char(
        related="stage_id.name",
        string="Etapa",
        store=True,
    )

    sale_subscription_line_ids = fields.One2many(
        comodel_name="sale.subscription.line",
        inverse_name="sale_subscription_id",
    )

    sale_order_ids_count = fields.Integer(
        compute="_compute_sale_order_ids_count", string="Sale orders"
    )

    account_invoice_ids_count = fields.Integer(
        compute="_compute_account_invoice_ids_count", string="Invoice Count"
    )

    limit_rule_count = fields.Integer(default=0, string="Subscription limit count")

    close_reason_id = fields.Many2one(
        comodel_name="sale.subscription.close.reason", string="Close Reason"
    )

    crm_team_id = fields.Many2one(comodel_name="crm.team", string="Sale team")

    to_renew = fields.Boolean(default=False, string="To renew")

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id_fpos(self):
        self.fiscal_position_id = (
            self.env["account.fiscal.position"]
            .with_company(self.company_id)
            .get_fiscal_position(self.partner_id.id)
        )

    def action_start_subscription(self):
        self.close_reason_id = False
        in_progress_stage = self.env["sale.subscription.stage"].search(
            [("type", "=", "in_progress")], limit=1
        )
        self.stage_id = in_progress_stage

    def action_close_subscription(self):
        self.recurring_next_date = False
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "close.reason.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": False,
        }

    def next_recurring_next_date(self, date_string):
        date_string = fields.Date.from_string(date_string)
        if self.template_id.recurring_rule_type == "days":
            date_string += relativedelta(days=+self.template_id.recurring_interval)
        elif self.template_id.recurring_rule_type == "weeks":
            date_string += relativedelta(weeks=+self.template_id.recurring_interval)
        elif self.template_id.recurring_rule_type == "months":
            date_string += relativedelta(months=+self.template_id.recurring_interval)
        else:
            date_string += relativedelta(years=+self.template_id.recurring_interval)
        return date_string

    def create_invoice(self):
        if not self.env["account.move"].check_access_rights("create", False):
            try:
                self.check_access_rights("write")
                self.check_access_rule("write")
            except AccessError:
                return self.env["account.move"]
        line_ids = []
        for line in self.sale_subscription_line_ids:
            account = (
                line.product_id.property_account_income_id
                or line.product_id.categ_id.property_account_income_categ_id
            )
            line_values = {
                "product_id": line.product_id.id,
                "name": line.name,
                "quantity": line.product_uom_qty,
                "price_unit": line.price_unit,
                "discount": line.discount,
                "price_subtotal": line.price_subtotal,
                "tax_ids": [(6, 0, line.tax_ids.ids)],
                "product_uom_id": line.product_id.uom_id.id,
                "account_id": account.id,
            }
            line_ids.append((0, 0, line_values))
        values = {
            "partner_id": self.partner_id.id,
            "invoice_date": self.recurring_next_date,
            "invoice_payment_term_id": self.partner_id.property_payment_term_id.id,
            "invoice_origin": self.name,
            "invoice_user_id": self.user_id.id,
            "partner_bank_id": self.company_id.partner_id.bank_ids[:1].id,
            "invoice_line_ids": line_ids,
        }
        if self.journal_id:
            values["journal_id"] = self.journal_id.id
        invoice_id = (
            self.env["account.move"]
            .sudo()
            .with_context(default_move_type="out_invoice", journal_type="sale")
            .create(values)
        )
        self.write({"invoice_ids": [(4, invoice_id.id)]})
        return invoice_id

    def create_sale_order(self):
        if not self.env["sale.order"].check_access_rights("create", False):
            try:
                self.check_access_rights("write")
                self.check_access_rule("write")
            except AccessError:
                return self.env["sale.order"]
        line_ids = []
        for line in self.sale_subscription_line_ids:
            tax = line.tax_ids
            line_values = {
                "product_id": line.product_id.id,
                "name": line.name,
                "product_uom_qty": line.product_uom_qty,
                "price_unit": line.price_unit,
                "discount": line.discount,
                "price_subtotal": line.price_subtotal,
                "tax_id": tax,
                "product_uom": line.product_id.uom_id.id,
            }
            line_ids.append((0, 0, line_values))
        values = {
            "partner_id": self.partner_id.id,
            "fiscal_position_id": self.fiscal_position_id.id,
            "date_order": datetime.now(),
            "payment_term_id": self.partner_id.property_payment_term_id.id,
            "user_id": self.user_id.id,
            "origin": self.name,
            "order_line": line_ids,
        }
        order_id = self.env["sale.order"].sudo().create(values)
        self.write({"sale_order_ids": [(4, order_id.id)]})
        return order_id

    def generate_invoice(self):
        invoice_number = ""
        msg_static = _("Created invoice with reference")
        if self.template_id.invoicing_mode in ["invoice", "invoice_send"]:
            invoice_id = self.create_invoice()
            invoice_id.action_post()
            if self.template_id.invoicing_mode == "invoice_send":
                mail_template_id = self.template_id.invoice_mail_template_id
                invoice_id.with_context(force_send=True).message_post_with_template(
                    mail_template_id.id,
                    composition_mode="comment",
                    email_layout_xmlid="mail.mail_notification_paynow",
                )
            invoice_number = invoice_id.name
            message_body = (
                "<b>%s</b> <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>"
                % (msg_static, invoice_id.id, invoice_number)
            )

        if self.template_id.invoicing_mode == "sale_and_invoice":
            order_id = self.create_sale_order()
            order_id.action_done()
            new_invoice_id = order_id._create_invoices()
            new_invoice_id.action_post()
            new_invoice_id.invoice_origin = order_id.name + ", " + self.name
            invoice_number = new_invoice_id.name
            message_body = (
                "<b>%s</b> <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>"
                % (msg_static, new_invoice_id.id, invoice_number)
            )
        if not invoice_number:
            invoice_number = _("To validate")
            message_body = "<b>%s</b> %s" % (msg_static, invoice_number)

        self.message_post(body=message_body)

    def manual_invoice(self):
        invoice_id = self.create_invoice()
        self._onchange_template_id()
        context = dict(self.env.context)
        context["form_view_initial_mode"] = "edit"
        return {
            "name": self.name,
            "views": [
                (self.env.ref("account.view_move_form").id, "form"),
                (self.env.ref("account.view_move_tree").id, "tree"),
            ],
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move",
            "res_id": invoice_id.id,
            "type": "ir.actions.act_window",
            "context": context,
        }

    @api.depends("invoice_ids", "sale_order_ids.invoice_ids")
    def _compute_account_invoice_ids_count(self):
        for record in self:
            record.account_invoice_ids_count = len(self.invoice_ids) + len(
                self.sale_order_ids.invoice_ids
            )

    def action_view_account_invoice_ids(self):
        return {
            "name": self.name,
            "views": [
                (self.env.ref("account.view_move_tree").id, "tree"),
                (self.env.ref("account.view_move_form").id, "form"),
            ],
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "domain": [
                ("id", "in", self.invoice_ids.ids + self.sale_order_ids.invoice_ids.ids)
            ],
            "context": self.env.context,
        }

    @api.depends("sale_order_ids")
    def _compute_sale_order_ids_count(self):
        for record in self:
            record.sale_order_ids_count = len(self.sale_order_ids)

    def action_view_sale_order_ids(self):
        active_ids = self.sale_order_ids.ids
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", active_ids)],
            "context": self.env.context,
        }

    def _check_dates(self, start, next_invoice):
        if start and next_invoice:
            date_start = start
            date_next_invoice = next_invoice
            if not isinstance(date_start, date) and not isinstance(
                date_next_invoice, date
            ):
                date_start = self.string2datetime(start)
                date_next_invoice = self.string2datetime(next_invoice)
            if date_start > date_next_invoice:
                return True
        return False

    def write(self, values):
        res = super().write(values)
        if "date_start" in values:
            for record in self:
                if record.template_id.recurring_rule_boundary == "limited":
                    values["date"] = (
                        relativedelta(months=+self.template_id.recurring_rule_count)
                        + record.date_start
                    )
                    if "recurring_next_date" in values:
                        check = record._check_dates(
                            values["date_start"], values["recurring_next_date"]
                        )
                        if check:
                            values["date_start"] = values["recurring_next_date"]
        if "stage_id" in values:
            for record in self:
                if record.stage_id:
                    if record.stage_id.type == "in_progress":
                        record.in_progress = True
                        record.date_start = date.today()
                    elif record.stage_id.type == "post":
                        record.close_reason_id = False
                        record.in_progress = False
                    else:
                        record.in_progress = False

        return res

    @api.model
    def create(self, values):
        if "recurring_rule_boundary" in values:
            if not values["recurring_rule_boundary"]:
                template_id = self.env["sale.subscription.template"].search(
                    [("id", "=", values["template_id"])]
                )
                date_start = values["date_start"]

                if not isinstance(values["date_start"], date):
                    date_start = self.string2datetime(values["date_start"])
                values["date"] = (
                    relativedelta(months=+template_id.recurring_rule_count) + date_start
                )
        if "date_start" in values and "recurring_next_date" in values:
            res = self._check_dates(values["date_start"], values["recurring_next_date"])
            if res:
                values["date_start"] = values["recurring_next_date"]
            values["stage_id"] = (
                self.env["sale.subscription.stage"]
                .search([("type", "=", "pre")], order="sequence desc")[-1]
                .id
            )
        return super(SaleSubscription, self).create(values)


class SaleSubscriptionLine(models.Model):
    _name = "sale.subscription.line"
    _description = "Subscription lines added to a given subscription"

    product_id = fields.Many2one(
        comodel_name="product.product",
        domain=[("sale_ok", "=", True)],
        string="Product",
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="sale_subscription_id.currency_id",
        store=True,
        readonly=True,
    )

    name = fields.Char(string="Description")

    product_uom_qty = fields.Float(default=1.0, string="Quantity")

    price_unit = fields.Float(string="Unit price")

    discount = fields.Float(string="Discount (%)")

    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        relation="subscription_line_tax",
        column1="subscription_line_id",
        column2="tax_id",
        string="Taxes",
    )

    @api.depends("product_id", "price_unit", "product_uom_qty", "discount", "tax_ids")
    def _compute_subtotal(self):
        for record in self:
            price = record.price_unit * (1 - (record.discount or 0.0) / 100.0)
            taxes = record.tax_ids.compute_all(
                price,
                record.currency_id,
                record.product_uom_qty,
                product=record.product_id,
                partner=record.sale_subscription_id.partner_id,
            )
            record.update(
                {
                    "amount_tax_line_amount": sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    ),
                    "price_total": taxes["total_included"],
                    "price_subtotal": taxes["total_excluded"],
                }
            )

    price_subtotal = fields.Monetary(
        string="Subtotal", readonly="True", compute=_compute_subtotal, store=True
    )

    price_total = fields.Monetary(
        string="Total", readonly="True", compute=_compute_subtotal, store=True
    )

    amount_tax_line_amount = fields.Float(
        string="Taxes Amount", compute="_compute_subtotal", store=True
    )

    sale_subscription_id = fields.Many2one(
        comodel_name="sale.subscription", string="Subscription"
    )
    company_id = fields.Many2one(
        related="sale_subscription_id.company_id",
        string="Company",
        store=True,
        index=True,
    )

    def _update_description(self):
        if not self.product_id:
            return
        lang = get_lang(self.env, self.sale_subscription_id.partner_id.lang).code
        product = self.product_id.with_context(
            lang=lang,
        )
        self.update(
            {
                "name": product.with_context(
                    lang=lang
                ).get_product_multiline_description_sale()
            }
        )

    @api.onchange("product_id")
    def product_id_change(self):
        if not self.product_id:
            return
        self._update_description()
        self._update_taxes()

    def _update_taxes(self):
        if not self.product_id:
            return

        self._compute_tax_id()

        if (
            self.sale_subscription_id.pricelist_id
            and self.sale_subscription_id.partner_id
        ):
            product = self.product_id.with_context(
                partner=self.sale_subscription_id.partner_id,
                quantity=self.product_uom_qty,
                date=fields.datetime.now(),
                pricelist=self.sale_subscription_id.pricelist_id.id,
                uom=self.product_id.uom_id.id,
            )
            self.update(
                {
                    "price_unit": product._get_tax_included_unit_price(
                        self.company_id,
                        self.sale_subscription_id.currency_id,
                        fields.datetime.now(),
                        "sale",
                        fiscal_position=self.sale_subscription_id.fiscal_position_id,
                        product_price_unit=self._get_display_price(product),
                        product_currency=self.sale_subscription_id.currency_id,
                    )
                }
            )

    @api.onchange("product_id", "price_unit", "product_uom_qty", "tax_ids")
    def _onchange_discount(self):
        if not (
            self.product_id
            and self.product_id.uom_id
            and self.sale_subscription_id.partner_id
            and self.sale_subscription_id.pricelist_id
            and self.sale_subscription_id.pricelist_id.discount_policy
            == "without_discount"
            and self.env.user.has_group("product.group_discount_per_so_line")
        ):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.sale_subscription_id.partner_id.lang,
            partner=self.sale_subscription_id.partner_id,
            quantity=self.product_uom_qty,
            date=fields.Datetime.now(),
            pricelist=self.sale_subscription_id.pricelist_id.id,
            uom=self.product_id.uom_id.id,
            fiscal_position=self.sale_subscription_id.fiscal_position_id
            or self.env.context.get("fiscal_position"),
        )

        price, rule_id = self.sale_subscription_id.pricelist_id.with_context(
            partner_id=self.sale_subscription_id.partner_id.id,
            date=fields.Datetime.now(),
            uom=self.product_id.uom_id.id,
        ).get_product_price_rule(
            self.product_id,
            self.product_uom_qty or 1.0,
            self.sale_subscription_id.partner_id,
        )
        new_list_price, currency = self.with_context(
            partner_id=self.sale_subscription_id.partner_id.id,
            date=fields.Datetime.now(),
            uom=self.product_id.uom_id.id,
        )._get_real_price_currency(
            product, rule_id, self.product_uom_qty, self.product_id.uom_id
        )

        if new_list_price != 0:
            if self.sale_subscription_id.pricelist_id.currency_id != currency:
                new_list_price = currency._convert(
                    new_list_price,
                    self.sale_subscription_id.pricelist_id.currency_id,
                    self.sale_subscription_id.company_id or self.env.company,
                    fields.Date.today(),
                )
            discount = (new_list_price - price) / new_list_price * 100
            if (discount > 0 and new_list_price > 0) or (
                discount < 0 and new_list_price < 0
            ):
                self.discount = discount

    def _get_real_price_currency(self, product, rule_id, qty, uom):
        PricelistItem = self.env["product.pricelist.item"]
        field_name = "lst_price"
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == "without_discount":
                while (
                    pricelist_item.base == "pricelist"
                    and pricelist_item.base_pricelist_id
                    and pricelist_item.base_pricelist_id.discount_policy
                    == "without_discount"
                ):
                    _price, rule_id = pricelist_item.base_pricelist_id.with_context(
                        uom=uom.id
                    ).get_product_price_rule(
                        product, qty, self.sale_subscription_id.partner_id
                    )
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == "standard_price":
                field_name = "standard_price"
                product_currency = product.cost_currency_id
            elif (
                pricelist_item.base == "pricelist" and pricelist_item.base_pricelist_id
            ):
                field_name = "price"
                product = product.with_context(
                    pricelist=pricelist_item.base_pricelist_id.id
                )
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(
                    product_currency,
                    currency_id,
                    self.company_id or self.env.company,
                    fields.Date.today(),
                )

        product_uom = self.env.context.get("uom") or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    def _get_display_price(self, product):
        if self.sale_subscription_id.pricelist_id.discount_policy == "with_discount":
            return product.with_context(
                pricelist=self.sale_subscription_id.pricelist_id.id,
                uom=self.product_id.uom_id.id,
            ).price

        final_price, rule_id = self.sale_subscription_id.pricelist_id.with_context(
            partner_id=self.sale_subscription_id.partner_id.id,
            date=fields.Datetime.now(),
            uom=self.product_id.uom_id.id,
        ).get_product_price_rule(
            product or self.product_id,
            self.product_uom_qty or 1.0,
            self.sale_subscription_id.partner_id,
        )
        base_price, currency = self.with_context(
            partner_id=self.sale_subscription_id.partner_id.id,
            date=fields.Datetime.now(),
            uom=self.product_id.uom_id.id,
        )._get_real_price_currency(
            product, rule_id, self.product_uom_qty, self.product_id.uom_id
        )
        if currency != self.sale_subscription_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price,
                self.sale_subscription_id.pricelist_id.currency_id,
                self.sale_subscription_id.company_id or self.env.company,
                fields.Date.today(),
            )
        return max(base_price, final_price)

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = (
                line.sale_subscription_id.fiscal_position_id
                or line.sale_subscription_id.fiscal_position_id.get_fiscal_position(
                    line.sale_subscription_id.partner_id.id
                )
            )
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(
                lambda t: t.company_id == line.env.company
            )
            line.tax_ids = fpos.map_tax(taxes)

# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleSubscriptionTemplate(models.Model):
    _name = "sale.subscription.template"
    _description = "Subscription templates"

    name = fields.Char(required=True)

    description = fields.Text(string="Terms and conditions")

    recurring_interval = fields.Integer(string="Repeat every", default=1)

    recurring_rule_type = fields.Selection(
        [
            ("days", "Day(s)"),
            ("weeks", "Week(s)"),
            ("months", "Month(s)"),
            ("years", "Year(s)"),
        ],
        string="Recurrence",
        default="months",
    )

    recurring_rule_boundary = fields.Selection(
        [("unlimited", "Forever"), ("limited", "Fixed")],
        string="Duration",
        default="unlimited",
    )

    invoicing_mode = fields.Selection(
        default="draft",
        string="Invoicing mode",
        selection=[
            ("draft", "Draft"),
            ("invoice", "Invoice"),
            ("invoice_send", "Invoice & send"),
            ("sale_and_invoice", "Sale order & Invoice"),
        ],
    )

    code = fields.Char()

    recurring_rule_count = fields.Integer(default=1, string="Rule count")

    invoice_mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Invoice Email",
        domain="[('model', '=', 'account.move')]",
    )

    product_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="subscription_template_id",
        string="Products",
    )

    product_ids_count = fields.Integer(
        compute="_compute_product_ids_count", string="product_ids"
    )

    subscription_ids = fields.One2many(
        comodel_name="sale.subscription",
        inverse_name="template_id",
        string="Subscriptions",
    )

    subscription_ids_count = fields.Integer(
        compute="_compute_subscription_ids_count", string="subscription_ids"
    )

    def _compute_subscription_ids_count(self):
        for subscription_ids in self:
            subscription_ids.subscription_ids_count = len(self.subscription_ids)

    def action_view_subscription_ids(self):
        return {
            "name": self.name,
            "view_mode": "tree,form",
            "res_model": "sale.subscription",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.subscription_ids.ids)],
        }

    @api.depends("product_ids")
    def _compute_product_ids_count(self):
        for record in self:
            record.product_ids_count = len(self.product_ids)

    def action_view_product_ids(self):
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "product.template",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.product_ids.ids)],
        }

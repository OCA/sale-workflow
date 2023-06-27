# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    subscription_ids = fields.One2many(
        comodel_name="sale.subscription",
        inverse_name="sale_order_id",
        string="Subscriptions",
    )

    subscriptions_count = fields.Integer(compute="_compute_subscriptions_count")

    order_subscription_id = fields.Many2one(
        comodel_name="sale.subscription", string="Subscription"
    )

    @api.depends("subscription_ids")
    def _compute_subscriptions_count(self):
        for subscriptions in self:
            subscriptions.subscriptions_count = len(self.subscription_ids)

    def action_view_subscriptions(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.subscription",
            "domain": [("id", "in", self.subscription_ids.ids)],
            "name": self.name,
            "view_mode": "tree,form",
        }

    def get_next_interval(self, type_interval, interval):
        date_start = date.today()
        if type_interval == "days":
            date_start += relativedelta(days=+interval)
        elif type_interval == "weeks":
            date_start += relativedelta(weeks=+interval)
        elif type_interval == "months":
            date_start += relativedelta(months=+interval)
        else:
            date_start += relativedelta(years=+interval)
        return date_start

    def create_subscription(self, lines, template_id):
        subscription_lines = []
        for line in lines:
            subscription_lines.append((0, 0, line.get_subscription_line_values()))

        if template_id:
            sub_id = self.env["sale.subscription"].create(
                {
                    "partner_id": self.partner_id.id,
                    "user_id": self._context["uid"],
                    "template_id": template_id.id,
                    "pricelist_id": self.partner_id.property_product_pricelist.id,
                    "date_start": date.today(),
                    "sale_order_id": self.id,
                    "sale_subscription_line_ids": subscription_lines,
                }
            )
            sub_id.action_start_subscription()
            self.subscription_ids = [(4, sub_id.id)]
            sub_id._onchange_template_id()
            sub_id.recurring_next_date = self.get_next_interval(
                template_id.recurring_rule_type, template_id.recurring_interval
            )

    def group_lines(self, order_lines):
        groups = defaultdict(list)
        for order_line in order_lines:
            groups[
                order_line.product_id.product_tmpl_id.subscription_template_id
            ].append(order_line)

        return groups.values()

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for record in self:
            groups = self.group_lines(
                record.order_line.filtered(lambda line: line.product_id.subscribable)
            )
            for group in groups:
                record.create_subscription(
                    group, group[0].product_id.product_tmpl_id.subscription_template_id
                )
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_subscription_line_values(self):
        return {
            "product_id": self.product_id.id,
            "name": self.product_id.name,
            "product_uom_qty": self.product_uom_qty,
            "price_unit": self.price_unit,
            "discount": self.discount,
            "price_subtotal": self.price_subtotal,
        }

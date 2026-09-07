# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import html

from odoo import api, fields, models
from odoo.api import Environment
from odoo.fields import Command
from odoo.tools import config


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "base.exception.method"]
    _name = "sale.order.line"

    exception_ids = fields.Many2many(
        "exception.rule", string="Exceptions", copy=False, readonly=True
    )
    exceptions_summary = fields.Html(
        readonly=True, compute="_compute_exceptions_summary"
    )
    ignore_exception = fields.Boolean(
        related="order_id.ignore_exception", store=True, string="Ignore Exceptions"
    )
    is_exception_danger = fields.Boolean(compute="_compute_is_exception_danger")

    @api.depends("exception_ids", "ignore_exception")
    def _compute_is_exception_danger(self):
        for rec in self:
            rec.is_exception_danger = (
                len(rec.exception_ids) > 0 and not rec.ignore_exception
            )

    @api.depends("exception_ids", "ignore_exception")
    def _compute_exceptions_summary(self):
        for rec in self:
            if rec.exception_ids and not rec.ignore_exception:
                rec.exceptions_summary = rec._get_exception_summary()
            else:
                rec.exceptions_summary = False

    def _get_exception_summary(self):
        items = "".join(
            f"<li>{html.escape(e.name)}: <i>{html.escape(e.description)}</i></li>"
            for e in self.exception_ids
        )
        return f"<ul>{items}</ul>"

    def _get_main_records(self):
        return self.mapped("order_id")

    @api.model
    def _reverse_field(self):
        return "sale_ids"

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        test_mode = config["test_enable"] and not self.env.context.get(
            "test_base_exception"
        )
        # Write exceptions in a new transaction to be committed so that we can
        #  rollback the ongoing one while keeping the exceptions stored
        with self.env.registry.cursor() as new_cr:
            new_env = (
                Environment(new_cr, self.env.uid, self.env.context)
                if not test_mode
                else self.env
            )
            lines_to_remove_exception = (self - records).filtered(
                lambda line: rule.id in line.exception_ids.ids
            )
            lines_to_remove_exception.with_env(new_env).exception_ids = [
                Command.unlink(rule.id)
            ]
            lines_to_add_exception = records.filtered(
                lambda line: rule.id not in line.exception_ids.ids
            )
            lines_to_add_exception.with_env(new_env).exception_ids = [
                Command.link(rule.id)
            ]
        return records.mapped("order_id")

    def _detect_exception_get_exc_class_values(self):
        res = super()._detect_exception_get_exc_class_values()
        return dict(res, target_model="sale.order")

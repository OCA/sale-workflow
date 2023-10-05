# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import html

from odoo import api, fields, models


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
        return "<ul>%s</ul>" % "".join(
            [
                "<li>%s: <i>%s</i></li>"
                % tuple(map(html.escape, (e.name, e.description)))
                for e in self.exception_ids
            ]
        )

    def _get_main_records(self):
        return self.mapped("order_id")

    @api.model
    def _reverse_field(self):
        return "sale_ids"

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        # Thanks to the new flush of odoo 13.0, queries will be optimized
        # together at the end even if we update the exception_ids many times.
        # On previous versions, this could be unoptimized.
        (self - records).exception_ids = [(3, rule.id)]
        records.exception_ids = [(4, rule.id)]
        return records.mapped("order_id")

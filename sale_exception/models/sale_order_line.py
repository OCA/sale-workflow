# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "base.exception.method"]
    _name = "sale.order.line"

    ignore_exception = fields.Boolean(
        related="order_id.ignore_exception", store=True, string="Ignore Exceptions"
    )

    def _get_main_records(self):
        return self.mapped("order_id")

    @api.model
    def _reverse_field(self):
        return "sale_ids"

    def _detect_exceptions(self, rule):
        records = super(SaleOrderLine, self)._detect_exceptions(rule)
        return records.mapped("order_id")

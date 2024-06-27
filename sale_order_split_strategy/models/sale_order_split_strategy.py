# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models
from odoo.osv.expression import AND
from odoo.tools.safe_eval import safe_eval


class SaleOrderSplitStrategy(models.Model):
    _name = "sale.order.split.strategy"
    _description = "Order split strategy"
    _order = "sequence,name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    line_filter_id = fields.Many2one(
        "ir.filters",
        domain="[('model_id', '=', 'sale.order.line')]",
        required=True,
    )
    copy_sections = fields.Boolean()
    remove_empty_sections_after_split = fields.Boolean()
    copy_notes = fields.Boolean()

    def _select_lines_to_split(self, orders):
        self.ensure_one()
        domain = self._get_lines_to_split_domain(orders)
        return self.env["sale.order.line"].search(domain).filtered(lambda li: not li._is_delivery())

    def _get_lines_to_split_domain(self, orders):
        domain = safe_eval(self.line_filter_id.domain)
        return AND([domain, [("order_id", "in", orders.ids)]])

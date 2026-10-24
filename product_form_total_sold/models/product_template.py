# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sales_total_count = fields.Float(
        string="Total Sold",
        compute="_compute_sales_total_count",
        digits="Product Unit of Measure",
    )

    @api.depends("product_variant_ids.sales_total_count")
    def _compute_sales_total_count(self):
        for template in self:
            template.sales_total_count = float_round(
                sum(
                    template.with_context(active_test=False).product_variant_ids.mapped(
                        "sales_total_count"
                    )
                ),
                precision_rounding=template.uom_id.rounding,
            )

    def action_view_sales_total(self):
        action = self.action_view_sales()
        action["context"].pop("search_default_filter_order_date", None)
        return action

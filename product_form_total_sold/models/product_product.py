# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    sales_total_count = fields.Float(
        string="Total Sold",
        compute="_compute_sales_total_count",
        digits="Product Unit of Measure",
    )

    def _compute_sales_total_count(self):
        self.sales_total_count = 0.0
        if not self.env.user.has_group("sales_team.group_sale_salesman"):
            return
        domain = [
            ("state", "in", self.env["sale.report"]._get_done_states()),
            ("product_id", "in", self.ids),
        ]
        qty_by_product = {
            product.id: qty
            for product, qty in self.env["sale.report"]._read_group(
                domain, ["product_id"], ["product_uom_qty:sum"]
            )
        }
        for product in self:
            if not product.id:
                continue
            product.sales_total_count = float_round(
                qty_by_product.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding,
            )

    def action_view_sales_total(self):
        action = self.action_view_sales()
        action["context"].pop("search_default_filter_order_date", None)
        return action

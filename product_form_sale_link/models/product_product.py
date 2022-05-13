# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    sale_lines_count = fields.Integer(
        compute="_compute_sale_lines_count", string="Sold"
    )

    def _compute_sale_lines_count(self):
        if not self.user_has_groups("sales_team.group_sale_salesman") or not self.ids:
            self.sale_lines_count = 0.0
            return
        domain = [
            ("state", "in", ["sale", "done"]),
            ("product_id", "in", self.ids),
            ("company_id", "in", self.env.companies.ids),
        ]
        sale_line_data = self.env["sale.order.line"].read_group(
            domain, ["product_id"], ["product_id"]
        )
        mapped_data = {
            m["product_id"][0]: m["product_id_count"] for m in sale_line_data
        }
        for product in self:
            product.sale_lines_count = mapped_data.get(product.id, 0)

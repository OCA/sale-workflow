# Copyright 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_optional_line_if_not_exists(self, product_template, price_unit):
        """Create optional product line if not exists"""
        self.ensure_one()
        sale_order_option_obj = self.env["sale.order.option"]
        if sale_order_option_obj.search_count(
            [
                ("order_id", "=", self.id),
                ("product_id.product_tmpl_id", "=", product_template.id),
            ]
        ):
            return
        return sale_order_option_obj.create(
            {
                "order_id": self.id,
                "price_unit": price_unit,
                "product_id": self.env["product.product"]
                .search(
                    [
                        ("product_tmpl_id", "=", product_template.id),
                    ]
                )[0]
                .id,
            }
        )

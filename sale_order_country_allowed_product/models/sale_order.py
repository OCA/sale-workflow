# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    unavailable_product_msg = fields.Html(compute="_compute_unavailable_product_msg")

    @api.depends("order_line.product_id")
    def _compute_unavailable_product_msg(self):
        for order in self:
            unavailable_product_msg = ""
            if any(not line.country_available for line in order.order_line):
                products = order.order_line.filtered(
                    lambda line: not line.country_available
                ).mapped("product_id")
                if products:
                    products_list = (
                        f'<ul>{"".join(f"<li>{p.name}</li>" for p in products)}</ul>'
                    )
                    unavailable_product_msg = _(
                        "The following products are not available in the shipping country: "
                        "%(products_list)s",
                        products_list=products_list,
                    )

            order.unavailable_product_msg = unavailable_product_msg

    def action_confirm(self):
        if any(
            not line.country_available for line in self.order_line
        ) and not self.env.user.has_group(
            "sale_order_country_allowed_product.ignore_country_sale"
        ):
            raise ValidationError(
                _(
                    "Sale order cannot be validated as some products are not available "
                    "in the shipping country."
                )
            )
        return super().action_confirm()

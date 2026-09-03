# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    unavailable_product_msg = fields.Html(
        compute="_compute_unavailable_product_msg",
        sanitize=False
    )

    @api.depends("order_line.product_id", "order_line.country_available")
    def _compute_unavailable_product_msg(self):
        for order in self:
            unavailable_product_msg = ""
            unavailable_products = order.order_line.filtered(
                lambda line: not line.country_available
            )
            products = unavailable_products.mapped("product_id")
            if products:
                list_items = "".join(f"<li>{p.display_name}</li>" for p in products)
                products_list = Markup(f"<ul>{list_items}</ul>")
                unavailable_product_msg = _(
                    "The following products are not available in the shipping country: "
                    "%(product_list)s",
                    product_list=products_list,
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

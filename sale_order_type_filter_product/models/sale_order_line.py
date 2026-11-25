# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains("product_id", "order_id")
    def _check_product_sale_order_type(self):
        for line in self:
            if not line.product_id or not line.order_id.type_id:
                continue
            allowed_types = line.product_id._get_allowed_sale_order_types()
            if allowed_types and line.order_id.type_id not in allowed_types:
                raise exceptions.ValidationError(
                    _(
                        "The product %(product)s is not allowed for "
                        "sale order type %(sale_order_type)s.",
                        product=line.product_id.display_name,
                        sale_order_type=line.order_id.type_id.display_name,
                    )
                )

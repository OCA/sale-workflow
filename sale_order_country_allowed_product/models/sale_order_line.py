# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    country_available = fields.Boolean(
        compute="_compute_country_available"
    )

    @api.depends(
        "product_id",
        "order_id.partner_shipping_id",
        "order_id.partner_shipping_id.country_id",
    )
    def _compute_country_available(self):
        for line in self:
            if not line.product_id:
                line.country_available = True
                continue

            allowed_countries = line.product_template_id.sale_allowed_country_ids
            shipping_country = line.order_id.partner_shipping_id.country_id
            line.country_available = (
                not allowed_countries
                or shipping_country in allowed_countries
            )

# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    country_available = fields.Boolean(compute="_compute_country_available")

    @api.depends("product_id", "order_id.partner_shipping_id")
    def _compute_country_available(self):
        for line in self:
            allowed_countries = line.product_id.sale_allowed_country_ids
            line.country_available = (
                not allowed_countries
                or line.order_id.partner_shipping_id.country_id.id
                in allowed_countries.ids
            )

# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    @api.depends_context(
        "pricelist",
        "partner",
        "quantity",
        "uom",
        "date",
        "no_variant_attributes_price_extra",
        "force_pricelist_date",
    )
    def _compute_product_price(self):
        # Just add force_pricelist_date in list of depends context
        return super()._compute_product_price()

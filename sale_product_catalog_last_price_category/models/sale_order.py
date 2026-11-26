# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_catalog_last_sale_lines(
        self, product_ids, groupby=("product_id",), use_delivery_address=False
    ):
        """Leave out the products whose category ignores the last sale price,
        so the catalog cards and the lines added from them keep the pricelist
        price. Every last price of the catalog, also the vendor cards of
        sale_product_catalog_supplierinfo, comes from these lines.
        """
        product_ids = (
            self.env["product.product"]
            .browse(product_ids)
            .filtered(lambda product: not product.categ_id.catalog_ignore_last_price)
            .ids
        )
        return super()._get_catalog_last_sale_lines(
            product_ids, groupby=groupby, use_delivery_address=use_delivery_address
        )

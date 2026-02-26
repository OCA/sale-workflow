# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController,
)


class WebsiteSaleProductConfiguratorMultipleController(
    WebsiteSaleProductConfiguratorController
):
    def _get_sale_multiple_vals(self, product_or_template):
        # Get product variant if we got a single variant template
        product = product_or_template
        if product._name == "product.template":
            product = product.product_variant_id

        if multiple_uom := product.sale_multiple_uom_id:
            return {
                "is_multiple": 1,
                "sale_multiple_qty": multiple_uom.factor,
            }
        return {
            "is_multiple": 0,
            "sale_multiple_qty": 1,
        }

    def _get_basic_product_information(
        self,
        product_or_template,
        pricelist,
        combination,
        currency=None,
        date=None,
        **kwargs,
    ):
        product_info = super()._get_basic_product_information(
            product_or_template,
            pricelist,
            combination,
            currency=currency,
            date=date,
            **kwargs,
        )
        product_info.update(self._get_sale_multiple_vals(product_or_template))
        return product_info

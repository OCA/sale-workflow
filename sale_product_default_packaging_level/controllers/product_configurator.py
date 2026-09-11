# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.sale.controllers.product_configurator import (
    SaleProductConfiguratorController,
)


class SaleProductConfiguratorPackagingController(SaleProductConfiguratorController):
    def _get_basic_product_information(
        self, product_or_template, pricelist, combination, **kwargs
    ):
        basic_information = super()._get_basic_product_information(
            product_or_template, pricelist, combination, **kwargs
        )
        basic_information = dict(
            **basic_information,
            default_product_packaging_level_name=product_or_template.from_default_level_packaging_id.name,
        )
        return basic_information

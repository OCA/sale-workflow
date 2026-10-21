# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_tax_included_unit_price_from_price(
        self,
        product_price_unit,
        product_taxes,
        fiscal_position=None,
        product_taxes_after_fp=None,
    ):
        pricelist_id = self.env.context.get("pricelist")
        if pricelist_id:
            pricelist = self.env["product.pricelist"].browse(pricelist_id)

            if product_taxes is None:
                product_taxes = self.taxes_id

            product_taxes = product_taxes._filter_taxes_by_company(
                self.env.company
            ).get_equivalent_tax(price_include=pricelist.price_include_taxes)

            if fiscal_position and pricelist.price_include_taxes:
                new_taxes = fiscal_position.map_tax(product_taxes)
                if all(new_taxes.mapped("price_include")):
                    # if new taxes are tax included with a pricelist in tax included
                    # we do not want do change the price unit so like before we
                    # do not pass the fiscal position
                    fiscal_position = None

        return super()._get_tax_included_unit_price_from_price(
            product_price_unit,
            product_taxes,
            fiscal_position=fiscal_position,
            product_taxes_after_fp=product_taxes_after_fp,
        )

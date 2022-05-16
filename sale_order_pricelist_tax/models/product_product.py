# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # TODO in V16 it will be better to refactor the odoo code
    @api.model
    def _get_tax_included_unit_price(
        self,
        company,
        currency,
        document_date,
        document_type,
        is_refund_document=False,
        product_uom=None,
        product_currency=None,
        product_price_unit=None,
        product_taxes=None,
        fiscal_position=None,
    ):
        pricelist_id = self.env.context.get("pricelist")
        if document_type == "sale" and pricelist_id:
            pricelist = self.env["product.pricelist"].browse(pricelist_id)
            if product_taxes is None and document_type == "sale":
                taxes = self.taxes_id.filtered(lambda x: x.company_id == company)
            else:
                taxes = product_taxes
            taxes._ensure_price_include()
            if fiscal_position:
                if not pricelist.price_include_taxes:
                    # if pricelist is tax exclude there is nothing to remove
                    # so we remove the fiscal position so the super method will
                    # not modify the price unit
                    fiscal_position = None
                else:
                    new_taxes = fiscal_position.map_tax(taxes)
                    if all(new_taxes.mapped("price_include")):
                        # if new taxes are tax included with a pricelist in tax included
                        # we do not want do change the price unit so like before we
                        # do not pass the fiscal position
                        fiscal_position = None

        return super()._get_tax_included_unit_price(
            company,
            currency,
            document_date,
            document_type,
            is_refund_document=is_refund_document,
            product_uom=product_uom,
            product_currency=product_currency,
            product_price_unit=product_price_unit,
            product_taxes=product_taxes,
            fiscal_position=fiscal_position,
        )

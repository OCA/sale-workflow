# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    def _compute_price_rule_multi(self, products_qty_partner, date=False, uom_id=False):
        force_pricelist_date = self.env.context.get("force_pricelist_date")
        if force_pricelist_date:
            date = force_pricelist_date
        return super()._compute_price_rule_multi(products_qty_partner, date, uom_id)

    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        force_pricelist_date = self.env.context.get("force_pricelist_date")
        if force_pricelist_date:
            date = force_pricelist_date
        return super()._compute_price_rule(products_qty_partner, date, uom_id)

    def get_products_price(
        self, products, quantities, partners, date=False, uom_id=False
    ):
        force_pricelist_date = self.env.context.get("force_pricelist_date")
        if force_pricelist_date:
            date = force_pricelist_date
        return super().get_products_price(products, quantities, partners, date, uom_id)

    def get_product_price(self, product, quantity, partner, date=False, uom_id=False):
        force_pricelist_date = self.env.context.get("force_pricelist_date")
        if force_pricelist_date:
            date = force_pricelist_date
        return super().get_product_price(product, quantity, partner, date, uom_id)

    def get_product_price_rule(
        self, product, quantity, partner, date=False, uom_id=False
    ):
        force_pricelist_date = self.env.context.get("force_pricelist_date")
        if force_pricelist_date:
            date = force_pricelist_date
        return super().get_product_price_rule(product, quantity, partner, date, uom_id)

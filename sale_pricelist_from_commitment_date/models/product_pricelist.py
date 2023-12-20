# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    def _get_product_rule(self, product, quantity, uom=None, date=False, **kwargs):
        force_pricelist_date = self.env.context.get("force_pricelist_date")
        if force_pricelist_date:
            date = force_pricelist_date
        return super()._get_product_rule(product, quantity, uom, date, **kwargs)

# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPricelistItem(models.Model):

    _inherit = "product.pricelist.item"

    def _compute_price(self, product, quantity, uom, date, currency=None):
        force_pricelist_date = self.env.context.get("force_pricelist_date")
        if force_pricelist_date:
            date = force_pricelist_date
        return super()._compute_price(product, quantity, uom, date, currency)

# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_product_price(self, product, quantity, uom=None, date=False, **kwargs):
        if "custom_base_price" in kwargs:
            return super(
                Pricelist,
                self.with_context(custom_base_price=kwargs["custom_base_price"]),
            )._get_product_price(product, quantity, uom, date, **kwargs)

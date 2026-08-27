# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_product_price(self, product, *args, **kwargs):
        """
        Overridden method to add custom_base_price
        to the context of recordset if it
        is specified in the kwargs
        """
        self = (
            self.with_context(custom_base_price=kwargs["custom_base_price"])
            if "custom_base_price" in kwargs
            else self
        )
        return super()._get_product_price(product, *args, **kwargs)

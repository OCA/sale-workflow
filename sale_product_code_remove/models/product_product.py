# Copyright 2023 Jarsa, (<https://www.jarsa.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_product_multiline_description_sale(self):
        name = super().get_product_multiline_description_sale()
        if self.default_code:
            name = name.replace(f"[{self.default_code}] ", "").strip()
        return name

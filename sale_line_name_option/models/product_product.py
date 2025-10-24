# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_product_multiline_description_sale(self):
        if self.env.company.no_product_code_in_sale_line_name:
            self = self.with_context(display_default_code=False)
        return super().get_product_multiline_description_sale()

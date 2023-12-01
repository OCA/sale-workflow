# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    def _find_suitable_product_packaging(self, product_qty, uom_id):
        """Find nothing if you want to keep what was there."""
        if self.env.context.get("keep_product_packaging"):
            return self.browse()
        return super()._find_suitable_product_packaging(product_qty, uom_id)

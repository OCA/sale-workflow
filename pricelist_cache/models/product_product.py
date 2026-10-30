# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model_create_multi
    def create(self, vals):
        """Create a cache record for each newly created product, for each global
        pricelist.
        """
        res = super().create(vals)
        pricelist_model = self.env["product.pricelist"]
        global_pricelist_ids = pricelist_model._get_global_pricelist_ids()
        if global_pricelist_ids and res:
            cache_model = self.env["product.pricelist.cache"]
            cache_model.with_delay().update_product_pricelist_cache(
                res.ids, global_pricelist_ids
            )
        return res

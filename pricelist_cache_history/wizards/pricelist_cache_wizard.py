# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

class PricelistCacheWizard(models.TransientModel):
    _inherit = "product.pricelist.cache.wizard"

    at_date = fields.Date(default=fields.Date.today())

    @api.onchange("pricelist_id", "product_id", "at_date")
    def _onchange_product_pricelist(self):
        super()._onchange_product_pricelist()

    def _get_cache_items_args(self):
        res = super()._get_cache_items_args()
        if not res:
            return res
        pricelist, products, kwargs = res
        kwargs["at_date"] = self.at_date or None
        return pricelist, products, kwargs

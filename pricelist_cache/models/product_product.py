# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    # This will be replaced by a new button in another PR.
    # def write(self, vals):
    #     """Updates pricelist cache when product price is modified.

    #     Only for pricelists where there's an item related to the modified product,
    #     or when the pricelist is global.
    #     A global pricelist have an item applied to all products is either:
    #      - not based on a parent pricelst (i.e. public pricelist)
    #      - based on a parent pricelist, and altering prices (i.e. factor pricelists)
    #        -> prices are those of the parent +20%
    #     """
    #     to_update_records = self.env["product.product"]
    #     # In order to not waste resources, only update cache when price have changed
    #     # Here, we determine if price has changed before using super()
    #     if "list_price" in vals:
    #         to_update_records = self.filtered(
    #             lambda r: r.list_price != vals["list_price"]
    #         )
    #     res = super().write(vals)
    #     if to_update_records:
    #         # Search pricelist items related to product, without fixed price
    #         items = self.env["product.pricelist.item"].search(
    #             [
    #                 ("product_id", "in", to_update_records.ids),
    #                 ("compute_price", "!=", "fixed"),
    #             ]
    #         )
    #         pricelist_ids_to_update = []
    #         # Skip items that are based on dates
    #         for item in items:
    #             # get all items in pricelist hierarchy tree
    #             items_tree = item.pricelist_id._recursive_get_items(self)
    #             if not items_tree._has_date_range():
    #                 pricelist_ids_to_update.append(item.pricelist_id.id)
    #         pricelist_model = self.env["product.pricelist"]
    #         # get global (see docstring) pricelists and add them
    #         global_pricelist_ids = pricelist_model._get_global_pricelist_ids()
    #         pricelist_ids_to_update.extend(global_pricelist_ids)
    #         if pricelist_ids_to_update:
    #             self.env[
    #                 "product.pricelist.cache"
    #             ].with_delay().update_product_pricelist_cache(
    #                 product_ids=to_update_records.ids,
    #                 pricelist_ids=list(set(pricelist_ids_to_update)),
    #             )
    #     return res

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

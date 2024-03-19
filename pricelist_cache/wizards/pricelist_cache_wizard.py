# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class PricelistCacheWizard(models.TransientModel):

    _name = "product.pricelist.cache.wizard"
    _description = "Wizard for pricelist cache"

    partner_id = fields.Many2one("res.partner")
    pricelist_id = fields.Many2one("product.pricelist")
    product_id = fields.Many2one("product.product")
    display_cache_line_ids = fields.Many2many(
        "product.pricelist.cache", string="Cached prices"
    )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.pricelist_id = self.partner_id.property_product_pricelist
        else:
            self.pricelist_id = False

    @api.onchange("pricelist_id", "product_id")
    def _onchange_product_pricelist(self):
        pricelist = self.pricelist_id
        product = self.product_id
        partner = self.partner_id
        if not pricelist:
            self.display_cache_line_ids = False
            return
        if product:
            products = product
        else:
            products = self.env["product.product"].search([])
        if partner and not partner.property_product_pricelist == pricelist:
            partner = False
        cache_model = self.env["product.pricelist.cache"]
        cache_selfs = cache_model.get_cached_prices_for_pricelist(
            self.pricelist_id, products
        )
        # TODO fields are flushed when get_cached_prices_for_pricelist
        # is called. I wonder is this is because of the use of flush()
        # in the code.
        # There's maybe a better way to keep those fields values.
        data = {
            "display_cache_line_ids": [(6, 0, cache_selfs.ids)],
            "pricelist_id": pricelist.id,
            "product_id": product.id if product else False,
            "partner_id": partner.id if partner else False,
        }
        self.update(data)

    def open_in_tree_view(self):
        prices = self.display_cache_line_ids
        cache_model = self.env["product.pricelist.cache"]
        domain = [("id", "in", prices.ids)]
        return cache_model._get_tree_view(domain)

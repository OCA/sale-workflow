# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, exceptions, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    is_pricelist_cache_available = fields.Boolean(
        related="property_product_pricelist.is_pricelist_cache_available"
    )

    def _default_pricelist_cache_product_filter_id(self):
        # When the module is installed, Odoo creates the new field and at the
        # same time tries to set the default value for all existing records in
        # the DB. However the XML data (and thus 'product_filter_default' filter)
        # is still not created at this stage.
        # In order to get the module installed, the 'raise_if_not_found' parameter
        # has been added, and to set the default value on existing partners
        # the post_init_hook 'set_default_partner_product_filter' has been defined.
        return self.env.ref(
            "pricelist_cache.product_filter_default", raise_if_not_found=False
        )

    pricelist_cache_product_filter_id = fields.Many2one(
        comodel_name="ir.filters",
        domain=[("model_id", "=", "product.product")],
        default=lambda o: o._default_pricelist_cache_product_filter_id(),
    )

    def _pricelist_cache_get_prices(self):
        if not self.is_pricelist_cache_available:
            raise exceptions.UserError(_("Pricelist caching in progress. Retry later"))
        pricelist = self._pricelist_cache_get_pricelist()
        products = self._pricelist_cache_get_products()
        cache_model = self.env["product.pricelist.cache"]
        return cache_model.get_cached_prices_for_pricelist(pricelist, products)

    def _pricelist_cache_get_pricelist(self):
        return self.property_product_pricelist

    def _pricelist_cache_get_products(self):
        domain = self._pricelist_cache_product_domain()
        return self.env["product.product"].search(domain)

    def _pricelist_cache_product_domain(self):
        if self.pricelist_cache_product_filter_id:
            return self.pricelist_cache_product_filter_id._get_eval_domain()
        return []

    def button_open_pricelist_cache_tree(self):
        prices = self._pricelist_cache_get_prices()
        cache_model = self.env["product.pricelist.cache"]
        domain = [("id", "in", prices.ids)]
        return cache_model._get_tree_view(domain)

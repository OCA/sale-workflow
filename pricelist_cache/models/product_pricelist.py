# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo import api, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            if record._is_factor_pricelist() or record._is_global_pricelist():
                product_ids_to_cache = None
            else:
                product_ids_to_cache = record.item_ids.mapped("product_id").ids
            cache_model = self.env["product.pricelist.cache"].with_delay()
            cache_model.update_product_pricelist_cache(
                product_ids=product_ids_to_cache, pricelist_ids=record.ids
            )
        return res

    def _get_product_prices(self, product_ids):
        self.ensure_one()
        # Search instead of browse, since products could have been unlinked
        # between the time where records have been created / modified
        # and the time this method is executed.
        products = self.env["product.product"].search([("id", "in", product_ids)])
        products_qty_partner = [(p, 1, False) for p in products]
        results = self._compute_price_rule(products_qty_partner, date.today())
        product_prices = {prod: price[0] for prod, price in results.items()}
        return product_prices

    def _get_root_pricelist_ids(self):
        """Returns the id of all root pricelists.

        A root pricelist have no item referencing another pricelist.
        """
        no_parent_query = """
            SELECT id
            FROM product_pricelist pp
            WHERE id NOT IN (
                SELECT pricelist_id
                FROM product_pricelist_item
                WHERE (
                    base_pricelist_id IS NOT NULL
                    AND base = 'pricelist'
                )
            );
        """
        self.flush()
        self.env.cr.execute(no_parent_query)
        return [row[0] for row in self.env.cr.fetchall()]

    def _get_factor_pricelist_ids(self):
        """Returns the id of all factor pricelists.

        A factor pricelist have an item referencing a pricelist,
        altering the price via price_discount or price_surcharge
        """
        factor_pricelist_query = """
            SELECT id
            FROM product_pricelist
            WHERE id IN (
                SELECT pricelist_id
                FROM product_pricelist_item
                WHERE (
                    base_pricelist_id IS NOT NULL
                    AND base = 'pricelist'
                    AND (
                        price_discount != 0.0
                        OR price_surcharge != 0.0
                    )
                )
            );
        """
        self.flush()
        self.env.cr.execute(factor_pricelist_query)
        return [row[0] for row in self.env.cr.fetchall()]

    def _get_global_pricelist_ids(self):
        """Return factor pricelists and pricelists with no parents."""
        global_pricelist_ids = self._get_root_pricelist_ids()
        factor_pricelist_ids = self._get_factor_pricelist_ids()
        return global_pricelist_ids + factor_pricelist_ids

    def _get_parent_pricelists(self):
        """Returns the parent pricelists.

        The parent pricelist is defined on a pricelist_item when it's applied
        globally, and based on another pricelist
        """
        self.ensure_one()
        parent_pricelist_items = self.item_ids.filtered(
            lambda i: (
                i.applied_on == "3_global"
                and i.base == "pricelist"
                and i.base_pricelist_id
            )
        )
        return parent_pricelist_items.mapped("base_pricelist_id")

    def _is_factor_pricelist(self):
        """Returns whether a pricelist is a factor pricelist.

        A factor pricelist is applied globally and refers to another pricelist.
        It also alters the "parent's price" by applying a discount or a surcharge
        on it.
        """
        self.ensure_one()
        parent_pricelist_items = self.item_ids.filtered(
            lambda i: (
                i.applied_on == "3_global"
                and i.base == "pricelist"
                and i.base_pricelist_id
                and (i.price_discount or i.price_surcharge)
            )
        )
        return bool(parent_pricelist_items)

    def _is_global_pricelist(self):
        """Returns whether a pricelist is a factor global.

        A factor pricelist is applied globally and refers to another pricelist.
        It also alters the "parent's price" by applying a discount or a surcharge
        on it.
        """
        self.ensure_one()
        return bool(not self._get_parent_pricelists())

    def _recursive_get_items(self, product):
        """Recursively searches on parent pricelists for items applied on product."""
        item_ids = self.item_ids.filtered(lambda i: i.product_id == product).ids
        for parent_pricelist in self._get_parent_pricelists():
            parent_items = parent_pricelist._recursive_get_items(product)
            item_ids.extend(parent_items.ids)
        return self.env["product.pricelist.item"].browse(item_ids)

    def button_open_pricelist_cache_tree(self):
        cache_model = self.env["product.pricelist.cache"]
        products = self.env["product.product"].search([])
        prices = cache_model.get_cached_prices_for_pricelist(self, products)
        domain = [("id", "in", prices.ids)]
        return cache_model._get_tree_view(domain)

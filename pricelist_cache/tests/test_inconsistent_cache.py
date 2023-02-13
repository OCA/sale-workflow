# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time

from odoo import exceptions

from .common import TestPricelistCacheCommon

CACHE_UNAVAILABLE_REGEX = r"Pricelist caching in progress. Retry later"


@freeze_time("2021-03-15")
class TestInconsistentCache(TestPricelistCacheCommon):
    """Pricelist cache uses the hierarchy between pricelists in order to save time
    during the build of the cache.
    For a given pricelist, we only store the prices that are defined on this specific
    pricelist. All other prices are retrieved from the parent pricelist (if any).
    Meaning that for this "tree":
        pricelistC ------> pricelistB -------> pricelistA
        - productC         - productB          - productA
                                               - productB
                                               - productC
    When retrieving all product prices for pricelist A,
    If only pricelist C has been cached, then only `pricelistC -> productC` would be
    returned.
    If only pricelist B is cached, then only the price for `pricelistB -> productB`
    would be returned.
    If only pricelistC is cached, then all prices are retrieved but are wrong, since
    those are the ones of pricelistC.

    To avoid that, we allow prices to be retrieved for a given pricelist, only
    if its whole hierarchy tree has been cached.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cache_model.flush_cache(cls.lists)
        cls.leave_pricelist = cls.list5
        cls.root_pricelist = cls.list0
        cls.partial_tree = cls.list1 | cls.list2 | cls.list3
        cls.partial_tree_head = cls.root_pricelist | cls.partial_tree
        cls.partial_tree_tail = cls.partial_tree | cls.leave_pricelist
        cls.complete_tree = cls.root_pricelist | cls.partial_tree | cls.leave_pricelist

    def test_tree_cached(self):
        # if the whole pricelist tree is cached, then all of its pricelists
        # has is_pricelist_cache_available = True
        self.cache_model.create_product_pricelist_cache(
            pricelist_ids=self.complete_tree.ids
        )
        self.assertTrue(all(self.complete_tree.mapped("is_pricelist_cache_available")))
        for pricelist in self.complete_tree:
            self.assertTrue(
                self.cache_model.get_cached_prices_for_pricelist(
                    pricelist, self.products
                )
            )

    def test_tail_tree(self):
        # if the root pricelist hasnt been computed, then no pricelist in the tree
        # has is_pricelist_cache_available = True
        self.cache_model.create_product_pricelist_cache(
            pricelist_ids=self.partial_tree_tail.ids
        )
        self.assertFalse(any(self.complete_tree.mapped("is_pricelist_cache_available")))
        for pricelist in self.complete_tree:
            with self.assertRaisesRegex(exceptions.UserError, CACHE_UNAVAILABLE_REGEX):
                self.cache_model.get_cached_prices_for_pricelist(
                    pricelist, self.products
                )

    def test_head_tree(self):
        # if the leave pricelist hasn't been computed, it isn't available, but all
        # head pricelists are.
        self.cache_model.create_product_pricelist_cache(
            pricelist_ids=self.partial_tree_head.ids
        )
        # All head tree prices have been cached. Only the leave_pricelist isn't avaible
        self.assertTrue(
            all(self.partial_tree_head.mapped("is_pricelist_cache_available"))
        )
        for pricelist in self.partial_tree_head:
            self.assertTrue(
                self.cache_model.get_cached_prices_for_pricelist(
                    pricelist, self.products
                )
            )
        # As cache is unavailable for leave_pricelist, an exception should be raised
        # when trying to retrieve its prices
        self.assertFalse(self.leave_pricelist.is_pricelist_cache_available)
        with self.assertRaisesRegex(exceptions.UserError, CACHE_UNAVAILABLE_REGEX):
            self.cache_model.get_cached_prices_for_pricelist(
                self.leave_pricelist, self.products
            )

    def test_missing_middle(self):
        # Caching only the head and the tail should only make the head available.
        self.cache_model.create_product_pricelist_cache(
            pricelist_ids=(self.root_pricelist | self.leave_pricelist).ids
        )
        self.assertTrue(self.root_pricelist.is_pricelist_cache_available)
        self.assertTrue(
            self.cache_model.get_cached_prices_for_pricelist(
                self.root_pricelist, self.products
            )
        )
        self.assertFalse(
            any(self.partial_tree_tail.mapped("is_pricelist_cache_available"))
        )
        for pricelist in self.partial_tree_tail:
            with self.assertRaisesRegex(exceptions.UserError, CACHE_UNAVAILABLE_REGEX):
                self.cache_model.get_cached_prices_for_pricelist(
                    pricelist, self.products
                )

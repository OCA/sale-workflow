# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from .common import TestPricelistCacheCommon, check_duplicates


@freeze_time("2021-03-15")
class TestPricelistCache(TestPricelistCacheCommon):
    @check_duplicates
    def test_base_caching(self):
        cache_model = self.cache_model
        # product 6, list 0: cached, price 100.0
        p6_list0_cache = cache_model.search(
            [
                ("product_id", "=", self.p6.id),
                ("pricelist_id", "=", self.list0.id),
            ]
        )
        self.assertTrue(p6_list0_cache)
        self.assertEqual(p6_list0_cache.price, 100.0)
        # product 6, list 1: cached, price 75
        p6_list1_cache = cache_model.search(
            [
                ("product_id", "=", self.p6.id),
                ("pricelist_id", "=", self.list1.id),
            ]
        )
        self.assertTrue(p6_list1_cache)
        self.assertEqual(p6_list1_cache.price, 75.0)
        # product 6, list 2 : Now cached, price 50.0
        p6_list2_cache = cache_model.search(
            [
                ("product_id", "=", self.p6.id),
                ("pricelist_id", "=", self.list2.id),
            ]
        )
        self.assertTrue(p6_list2_cache)
        self.assertEqual(p6_list2_cache.price, 50.0)
        # product 6, list 3 : Cached, price 25.0
        p6_list3_cache = cache_model.search(
            [
                ("product_id", "=", self.p6.id),
                ("pricelist_id", "=", self.list3.id),
            ]
        )
        self.assertTrue(p6_list3_cache)
        self.assertEqual(p6_list3_cache.price, 25.0)
        # product 6, list 4 : Cached, price 25.0
        p6_list4_cache = cache_model.search(
            [
                ("product_id", "=", self.p6.id),
                ("pricelist_id", "=", self.list4.id),
            ]
        )
        self.assertTrue(p6_list4_cache)
        self.assertEqual(p6_list4_cache.price, 15.0)
        # product 6, list 5 : Cached, list3 price + 20
        p6_list3_cache = cache_model.search(
            [
                ("product_id", "=", self.p6.id),
                ("pricelist_id", "=", self.list3.id),
            ]
        )
        expected_price = p6_list3_cache.price + 20.0
        p6_list5_cache = cache_model.search(
            [
                ("product_id", "=", self.p6.id),
                ("pricelist_id", "=", self.list5.id),
            ]
        )
        self.assertTrue(p6_list5_cache)
        self.assertEqual(p6_list5_cache.price, expected_price)
        # product 7, list 3: cached, price 50.0
        p7_list4_cache = cache_model.search(
            [
                ("product_id", "=", self.p7.id),
                ("pricelist_id", "=", self.list4.id),
            ]
        )
        self.assertTrue(p7_list4_cache)
        self.assertEqual(p7_list4_cache.price, 50.0)
        # product 7, list 5 : Cached, list0 price + 20
        p7_list0_cache = cache_model.search(
            [
                ("product_id", "=", self.p7.id),
                ("pricelist_id", "=", self.list0.id),
            ]
        )
        expected_price = p7_list0_cache.price + 20.0
        p7_list5_cache = cache_model.search(
            [
                ("product_id", "=", self.p7.id),
                ("pricelist_id", "=", self.list5.id),
            ]
        )
        self.assertTrue(p7_list5_cache)
        self.assertEqual(p7_list5_cache.price, expected_price)
        # product 8, list 0: cached price 100.0
        p8_list0_cache = cache_model.search(
            [
                ("product_id", "=", self.p8.id),
                ("pricelist_id", "=", self.list0.id),
            ]
        )
        self.assertTrue(p8_list0_cache)
        self.assertEqual(p8_list0_cache.price, 100.0)

    @check_duplicates
    def test_retrieve_price_list(self):
        products = self.products
        cache_model = self.cache_model
        # list0 cache
        l0_cache = cache_model.get_cached_prices_for_pricelist(self.list0, products)
        self.assertEqual(len(l0_cache), 4)
        l0_p6_cache = l0_cache.filtered(lambda c: c.product_id == self.p6)
        self.assertEqual(l0_p6_cache.price, 100.0)
        l0_p8_cache = l0_cache.filtered(lambda c: c.product_id == self.p8)
        self.assertEqual(l0_p6_cache.price, 100.0)
        # list1 cache
        l1_cache = cache_model.get_cached_prices_for_pricelist(self.list1, products)
        self.assertEqual(len(l1_cache), 4)
        l1_p6_cache = l1_cache.filtered(lambda c: c.product_id == self.p6)
        self.assertEqual(l1_p6_cache.price, 75.0)
        # p8 price should have been fetched from list0 cache.
        l1_p8_cache = l1_cache.filtered(lambda c: c.product_id == self.p8)
        self.assertEqual(l0_p8_cache, l1_p8_cache)
        # list2 cache
        l2_cache = cache_model.get_cached_prices_for_pricelist(self.list2, products)
        self.assertEqual(len(l2_cache), 4)
        l2_p6_cache = l2_cache.filtered(lambda c: c.product_id == self.p6)
        self.assertEqual(l2_p6_cache.price, 50.0)
        # p8 price should have been fetched from list0 cache.
        l2_p8_cache = l2_cache.filtered(lambda c: c.product_id == self.p8)
        self.assertEqual(l0_p8_cache, l2_p8_cache)
        # list3 cache
        l3_cache = cache_model.get_cached_prices_for_pricelist(self.list3, products)
        self.assertEqual(len(l3_cache), 4)
        l3_p6_cache = l3_cache.filtered(lambda c: c.product_id == self.p6)
        self.assertEqual(l3_p6_cache.price, 25.0)
        # p8 price should have been fetched from list0 cache.
        l3_p8_cache = l3_cache.filtered(lambda c: c.product_id == self.p8)
        self.assertEqual(l0_p8_cache, l3_p8_cache)
        # list4 cache
        l4_cache = cache_model.get_cached_prices_for_pricelist(self.list4, products)
        self.assertEqual(len(l4_cache), 4)
        l4_p6_cache = l4_cache.filtered(lambda c: c.product_id == self.p6)
        self.assertEqual(l4_p6_cache.price, 15.0)
        l4_p7_cache = l4_cache.filtered(lambda c: c.product_id == self.p7)
        self.assertEqual(l4_p7_cache.price, 50.0)
        # p8 price should have been fetched from list0 cache.
        l4_p8_cache = l4_cache.filtered(lambda c: c.product_id == self.p8)
        self.assertEqual(l0_p8_cache, l4_p8_cache)

    @check_duplicates
    def test_pricelist_methods(self):
        # test _get_root_pricelist_ids
        pricelist_model = self.env["product.pricelist"]
        expected_root_pricelist_ids = [
            self.list0.id,
            self.env.ref("product.list0").id,
        ]
        # This pricelist is created when stock module is installed. No other
        # way is found yet to identify it.
        pl = pricelist_model.search([("name", "=", "Default USD pricelist")])
        if pl:
            expected_root_pricelist_ids.append(pl.id)
        expected_root_pricelist_ids.sort()
        root_pricelist_ids = pricelist_model._get_root_pricelist_ids()
        root_pricelist_ids.sort()
        self.assertEqual(root_pricelist_ids, expected_root_pricelist_ids)
        # test _get_factor_pricelist_ids
        expected_factor_pricelist_ids = self.list5.ids
        factor_pricelist_ids = pricelist_model._get_factor_pricelist_ids()
        self.assertEqual(factor_pricelist_ids, expected_factor_pricelist_ids)
        # test _get_parent_pricelists
        list_5_parent = self.list5._get_parent_pricelists()
        self.assertEqual(list_5_parent, self.list3)
        list_4_parent = self.list4._get_parent_pricelists()
        self.assertEqual(list_4_parent, self.list0)
        list_3_parent = self.list3._get_parent_pricelists()
        self.assertEqual(list_3_parent, self.list2)
        list_2_parent = self.list2._get_parent_pricelists()
        self.assertEqual(list_2_parent, self.list1)
        list_1_parent = self.list1._get_parent_pricelists()
        self.assertEqual(list_1_parent, self.list0)
        list_0_parent = self.list0._get_parent_pricelists()
        self.assertFalse(list_0_parent)
        # test _is_factor_pricelist
        factor_pricelist = pricelist_model.browse(factor_pricelist_ids)
        self.assertTrue(factor_pricelist._is_factor_pricelist())
        root_pricelists = pricelist_model.browse(root_pricelist_ids)
        self.assertEqual(len(root_pricelists), len(expected_root_pricelist_ids))
        for pricelist in root_pricelists:
            self.assertFalse(pricelist._is_factor_pricelist())
        # test _recursive_get_items
        expected_item_ids = [
            self.env.ref("pricelist_cache.item2").id,
            self.env.ref("pricelist_cache.item5").id,
            self.env.ref("pricelist_cache.item7").id,
            self.env.ref("pricelist_cache.item9").id,
        ]
        expected_item_ids.sort()
        items = self.list3._recursive_get_items(self.p6)
        item_ids = items.ids
        item_ids.sort()
        self.assertEqual(item_ids, expected_item_ids)
        # test _has_date_range
        self.assertTrue(items._has_date_range())
        items -= self.env.ref("pricelist_cache.item7")
        self.assertFalse(items._has_date_range())
        # test _get_pricelist_products_group
        expected_groups = {
            self.list0.id: self.p6.ids,
            self.list1.id: self.p6.ids,
            self.list3.id: self.p6.ids,
        }
        groups = items._get_pricelist_products_group()
        for (
            expected_pricelist_id,
            expected_product_ids,
        ) in expected_groups.items():
            self.assertEqual(expected_product_ids, groups[expected_pricelist_id])

    @check_duplicates
    @freeze_time("2021-04-15")
    def test_cache_at_product_create(self):
        """Ensures that cache prices are created at product creation on each global
        pricelist."""
        # TODO: Add the required dependencies in a future release
        # Stock is a dependency for the creation of this product
        new_product = self.env["product.product"].create(
            {"name": "Dehydrated Water", "list_price": 42}
        )
        # global pricelist, cache created, regular price
        list0_cache = self.cache_model.search(
            [
                ("product_id", "=", new_product.id),
                ("pricelist_id", "=", self.list0.id),
            ]
        )
        self.assertTrue(list0_cache)
        self.assertEqual(list0_cache.price, 42)
        # Not a global pricelist, not defined
        global_ids = [self.list1.id, self.list2.id, self.list3.id, self.list4.id]
        not_global_lists_cache = self.cache_model.search(
            [
                ("product_id", "=", new_product.id),
                ("pricelist_id", "in", global_ids),
            ]
        )
        self.assertFalse(not_global_lists_cache)
        # Factor pricelist, defined, price +20
        list5_cache = self.cache_model.search(
            [
                ("product_id", "=", new_product.id),
                ("pricelist_id", "=", self.list5.id),
            ]
        )
        self.assertTrue(list5_cache)
        self.assertEqual(list5_cache.price, 62)

    @check_duplicates
    @freeze_time("2021-04-15")
    def test_cache_at_pricelist_create(self):
        # create pricelist child of list0, no item, no cache created
        pricelist_model = self.env["product.pricelist"]
        pricelist = pricelist_model.create(
            {
                "name": "test1",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "pricelist",
                            "base_pricelist_id": self.list0.id,
                        },
                    )
                ],
            }
        )
        cached_prices = self.cache_model.search([("pricelist_id", "=", pricelist.id)])
        self.assertFalse(cached_prices)
        # create pricelist child of list0, 1 item, 1 cache create
        pricelist = pricelist_model.create(
            {
                "name": "test2",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "pricelist",
                            "base_pricelist_id": self.list0.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "applied_on": "0_product_variant",
                            "base": "list_price",
                            "product_id": self.p6.id,
                            "fixed_price": 16.0,
                        },
                    ),
                ],
            }
        )
        cached_prices = self.cache_model.search([("pricelist_id", "=", pricelist.id)])
        self.assertEqual(len(cached_prices), 1)
        self.assertEqual(cached_prices.price, 16.0)
        # create factor pricelist +30, compare price with parent pricelist
        pricelist = pricelist_model.create(
            {
                "name": "test3",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "pricelist",
                            "base_pricelist_id": self.list0.id,
                            "price_surcharge": 30,
                        },
                    )
                ],
            }
        )
        self.assertTrue(pricelist._is_factor_pricelist())
        for product in self.products:
            l0_cache = self.cache_model.search(
                [
                    ("pricelist_id", "=", self.list0.id),
                    ("product_id", "=", product.id),
                ]
            )
            cache = self.cache_model.search(
                [
                    ("pricelist_id", "=", pricelist.id),
                    ("product_id", "=", product.id),
                ]
            )
            self.assertEqual(l0_cache.price + 30, cache.price)
        # create root pricelist, prices should be the same than those returned
        # by pricelist._compute_price_rule()
        pricelist = pricelist_model.create({"name": "test4"})
        self.assertTrue(pricelist._is_global_pricelist())
        product_prices = pricelist._get_product_prices(self.products.ids)
        for product_id, price in product_prices.items():
            cache = self.cache_model.search(
                [
                    ("product_id", "=", product_id),
                    ("pricelist_id", "=", pricelist.id),
                ]
            )
            self.assertEqual(cache.price, price)

    @check_duplicates
    def test_reset_cache(self):
        """Ensures that the sequence is reset when cache is reset, to avoid reaching
        the limit of ids, since the id is an int, with hard limit to 2,147,483,627.
        """
        old_max_cache_id = max(self.cache_model.search([]).ids)
        self.cache_model.cron_reset_pricelist_cache()
        new_max_cache_id = max(self.cache_model.search([]).ids)
        self.assertEqual(new_max_cache_id, old_max_cache_id)

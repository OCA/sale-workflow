# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from freezegun import freeze_time

from .common import TestPricelistCacheCommon


@freeze_time("2021-03-15")
class TestPricelistCache(TestPricelistCacheCommon):
    # @check_duplicates
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
        p6_list1_cache = cache_model.get_cached_prices_for_pricelist(
            self.list1, self.p6
        )
        self.assert_cache(p6_list1_cache, [75.0])
        # product 6, list 2 : Now cached, price 50.0
        p6_list2_cache = cache_model.get_cached_prices_for_pricelist(
            self.list2, self.p6
        )
        self.assert_cache(p6_list2_cache, [50.0])
        # product 6, list 3 : Cached, price 25.0
        p6_list3_cache = cache_model.get_cached_prices_for_pricelist(
            self.list3, self.p6
        )
        self.assert_cache(p6_list3_cache, [25.0])
        # product 6, list 4 : Cached, price 25.0
        p6_list4_cache = cache_model.get_cached_prices_for_pricelist(
            self.list4, self.p6
        )
        self.assert_cache(p6_list4_cache, [15.0])
        # product 6, list 5 : Cached, list3 price + 20
        expected_price = p6_list3_cache.price + 20.0
        p6_list5_cache = cache_model.get_cached_prices_for_pricelist(
            self.list5, self.p6
        )
        self.assert_cache(p6_list5_cache, [expected_price])
        # product 7, list 3: cached, price 50.0
        p7_list4_cache = cache_model.get_cached_prices_for_pricelist(
            self.list4, self.p7
        )
        self.assert_cache(p7_list4_cache, [50.0])
        # product 7, list 5 : Cached, list0 price + 20
        p7_list0_cache = cache_model.get_cached_prices_for_pricelist(
            self.list0, self.p7
        )
        expected_price = p7_list0_cache.price + 20.0
        p7_list5_cache = cache_model.get_cached_prices_for_pricelist(
            self.list5, self.p7
        )
        self.assert_cache(p7_list5_cache, [expected_price])
        # product 8, list 0: cached price 100.0
        p8_list0_cache = cache_model.get_cached_prices_for_pricelist(
            self.list0, self.p8
        )
        self.assert_cache(p8_list0_cache, [100.0])

    # TODO with pricelist_cache_history, we might have duplicates according
    # to this decorator's definition
    # @check_duplicates
    def test_retrieve_price_list(self):
        products = self.products
        cache_model = self.cache_model
        # list0 cache
        l0_cache = cache_model.get_cached_prices_for_pricelist(self.list0, products)
        self.assertEqual(len(l0_cache), 4)
        l0_p6_cache = l0_cache.filtered(lambda c: c.product_id == self.p6)
        l0_p8_cache = l0_cache.filtered(lambda c: c.product_id == self.p8)
        self.assert_cache(l0_p6_cache | l0_p8_cache, [100.0, 100.0])
        # list1 cache
        l1_cache = cache_model.get_cached_prices_for_pricelist(self.list1, products)
        self.assertEqual(len(l1_cache), 4)
        l1_p6_cache = l1_cache.filtered(lambda c: c.product_id == self.p6)
        l1_p8_cache = l1_cache.filtered(lambda c: c.product_id == self.p8)
        # p8 price should have been fetched from list0 cache.
        self.assertEqual(l1_p8_cache, l0_p8_cache)
        self.assert_cache(l1_p6_cache | l1_p8_cache, [75.0, 100.0])
        # list2 cache
        l2_cache = cache_model.get_cached_prices_for_pricelist(self.list2, products)
        self.assertEqual(len(l2_cache), 4)
        l2_p6_cache = l2_cache.filtered(lambda c: c.product_id == self.p6)
        l2_p8_cache = l2_cache.filtered(lambda c: c.product_id == self.p8)
        # p8 price should have been fetched from list0 cache.
        self.assertEqual(l0_p8_cache, l2_p8_cache)
        self.assert_cache(l2_p6_cache | l2_p8_cache, [50.0, 100.0])
        # list3 cache
        l3_cache = cache_model.get_cached_prices_for_pricelist(self.list3, products)
        self.assertEqual(len(l3_cache), 4)
        l3_p6_cache = l3_cache.filtered(lambda c: c.product_id == self.p6)
        l3_p8_cache = l3_cache.filtered(lambda c: c.product_id == self.p8)
        # p8 price should have been fetched from list0 cache.
        self.assertEqual(l0_p8_cache, l3_p8_cache)
        self.assert_cache(l3_p6_cache | l3_p8_cache, [25.0, 100])
        # list4 cache
        l4_cache = cache_model.get_cached_prices_for_pricelist(self.list4, products)
        self.assertEqual(len(l4_cache), 4)
        l4_p6_cache = l4_cache.filtered(lambda c: c.product_id == self.p6)
        l4_p7_cache = l4_cache.filtered(lambda c: c.product_id == self.p7)
        l4_p8_cache = l4_cache.filtered(lambda c: c.product_id == self.p8)
        # p8 price should have been fetched from list0 cache.
        self.assertEqual(l0_p8_cache, l4_p8_cache)
        self.assert_cache(l4_p6_cache | l4_p7_cache | l4_p8_cache, [15.0, 50.0, 100.0])

    # @check_duplicates
    def test_pricelist_methods(self):
        # test _get_root_pricelist_ids
        pricelist_model = self.env["product.pricelist"]
        # We only check that the pricelists created by this module
        # are the root pricelists recordset.
        # There's already a few created by odoo, another one created
        # by pricelist_cache_history.
        expected_root_pricelist_ids = [
            self.list0.id,
        ]
        root_pricelist_ids = pricelist_model._get_root_pricelist_ids()
        for expected_root_pricelist_id in expected_root_pricelist_ids:
            self.assertIn(expected_root_pricelist_id, root_pricelist_ids)
        # Same thing here, only check that factor pricelists created by
        # this module are retrieved by _get_factor_pricelist_ids
        expected_factor_pricelist_ids = [
            self.list5.id,
        ]
        factor_pricelist_ids = pricelist_model._get_factor_pricelist_ids()
        for expected_factor_pricelist_id in expected_factor_pricelist_ids:
            self.assertIn(expected_factor_pricelist_id, factor_pricelist_ids)
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

    # @check_duplicates
    @freeze_time("2021-04-15")
    def test_cache_at_product_create(self):
        """Ensures that cache prices are created at product creation on each global
        pricelist."""
        cache_model = self.cache_model
        # TODO: Add the required dependencies in a future release
        # Stock is a dependency for the creation of this product
        new_product = self.env["product.product"].create(
            {"name": "Dehydrated Water", "list_price": 42}
        )
        # global pricelist, cache created, regular price
        cache_model.get_cached_prices_for_pricelist(self.list2, self.p6)
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
        cache_model.get_cached_prices_for_pricelist(self.list2, self.p6)
        not_global_lists_cache = self.cache_model.search(
            [
                ("product_id", "=", new_product.id),
                ("pricelist_id", "in", global_ids),
            ]
        )
        self.assertFalse(not_global_lists_cache)
        # Factor pricelist, defined, price +20
        cache_model.get_cached_prices_for_pricelist(self.list2, self.p6)
        list5_cache = self.cache_model.search(
            [
                ("product_id", "=", new_product.id),
                ("pricelist_id", "=", self.list5.id),
            ]
        )
        self.assertTrue(list5_cache)
        self.assertEqual(list5_cache.price, 62)

    # @check_duplicates
    @freeze_time("2021-04-15")
    def test_cache_at_pricelist_create(self):
        # create pricelist child of list0, no item, no cache created
        pricelist_model = self.env["product.pricelist"]
        cache_model = self.cache_model
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
            cache_model.get_cached_prices_for_pricelist(self.list2, self.p6)
            l0_cache = self.cache_model.search(
                [
                    ("pricelist_id", "=", self.list0.id),
                    ("product_id", "=", product.id),
                ]
            )
            cache_model.get_cached_prices_for_pricelist(self.list2, self.p6)
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
        today = date.today()
        product_prices = pricelist._get_product_prices(self.products.ids, today)
        for product_id, price in product_prices.items():
            cache_model.get_cached_prices_for_pricelist(self.list2, self.p6)
            cache = self.cache_model.search(
                [
                    ("product_id", "=", product_id),
                    ("pricelist_id", "=", pricelist.id),
                ]
            )
            self.assertEqual(cache.price, price)

    # @check_duplicates
    def test_reset_cache(self):
        """Ensures that the sequence is reset when cache is reset, to avoid reaching
        the limit of ids, since the id is an int, with hard limit to 2,147,483,627.
        """
        old_max_cache_id = max(self.cache_model.search([]).ids)
        self.cache_model.cron_reset_pricelist_cache()
        new_max_cache_id = max(self.cache_model.search([]).ids)
        self.assertEqual(new_max_cache_id, old_max_cache_id)

    # @check_duplicates
    def test_create_new_cache__from_product_create(self):
        # Case 1, I create a new product, price should be available from each pricelist
        cache_model = self.cache_model
        p7 = self.env["product.product"].create(
            {
                "name": "Test Product",
                "price": 42.0,
            }
        )
        expected_prices = [
            (self.list0, 42.0),
            (self.list1, 42.0),
            (self.list2, 42.0),
            (self.list3, 42.0),
            (self.list4, 42.0),
            (self.list5, 62.0),  # Because of the 20.0 surcharge
        ]
        for pricelist, expected_price in expected_prices:
            cached_price = cache_model.get_cached_prices_for_pricelist(pricelist, p7)
            self.assertEqual(cached_price.price, expected_price)

    # @check_duplicates
    def test_create_new_cache__from_pricelist_create_without_item(self):
        cache_model = self.cache_model
        # Prices from list0 aren't altered, so they can be used here as
        # the expected prices
        data = {"name": "list_test"}
        test_list = self.env["product.pricelist"].create(data)
        product_ids = self.products.ids
        # test list has no parent, therefore, those prices are the unaltered ones
        # directly coming from the products.
        # see odoo/src/addons/product/data/product_demo.xml
        expected_prices = [
            {"id": 17, "price": 320.0},
            {"id": 18, "price": 79.0},
            {"id": 19, "price": 1799.0},
            {"id": 20, "price": 47.0},
        ]
        # We use search here. As the mechanism that retrieves prices might fetch
        # prices from a parent pricelist and we want to ensure it actually
        # created cache records. Belt and braces.
        prices = cache_model.search(
            [
                ("pricelist_id", "=", test_list.id),
                ("product_id", "in", product_ids),
            ]
        )
        self.assertEqual(len(prices), len(product_ids))
        # Now check that prices are ok
        cache_records = cache_model.get_cached_prices_for_pricelist(
            test_list, self.products
        )
        prices = [{"id": c.product_id.id, "price": c.price} for c in cache_records]
        prices.sort(key=lambda r: r["id"])
        self.assertEqual(prices, expected_prices)
        # Now, since we do not update cache during two cache reset, creating
        # a pricelist item with a new price shouldn't be reflected in the cache
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": test_list.id,
                "applied_on": "0_product_variant",
                "base": "list_price",
                "product_id": self.p6.id,
                "fixed_price": 42.0,
            }
        )
        cache_record = cache_model.get_cached_prices_for_pricelist(test_list, self.p6)
        self.assertEqual(cache_record.price, 320.0)
        # However, if the cache is reset, the new price is correctly reset
        self.cache_model.cron_reset_pricelist_cache()
        cache_record = cache_model.get_cached_prices_for_pricelist(test_list, self.p6)
        self.assertEqual(cache_record.price, 42.0)

    # @check_duplicates
    def test_create_new_cache__from_pricelist_create_with_item(self):
        cache_model = self.cache_model
        # We create a pricelist and its item at once, cache should be created with
        # the prices specified on the items.
        item_values = {
            "applied_on": "0_product_variant",
            "base": "list_price",
            "product_id": self.p6.id,
            "fixed_price": 42.0,
        }
        pricelist_values = {"name": "list_test", "item_ids": [(0, 0, item_values)]}
        test_list = self.env["product.pricelist"].create(pricelist_values)
        expected_prices = [
            # Only this is different from the previous test
            {"id": 17, "price": 42.0},
            {"id": 18, "price": 79.0},
            {"id": 19, "price": 1799.0},
            {"id": 20, "price": 47.0},
        ]
        # Now check that prices are ok
        cache_records = cache_model.get_cached_prices_for_pricelist(
            test_list, self.products
        )
        prices = [{"id": c.product_id.id, "price": c.price} for c in cache_records]
        prices.sort(key=lambda r: r["id"])
        self.assertEqual(prices, expected_prices)

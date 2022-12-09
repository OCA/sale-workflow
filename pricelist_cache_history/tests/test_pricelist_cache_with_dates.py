# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date, timedelta

from freezegun import freeze_time

from .common import TestPricelistCacheHistoryCommonCase


@freeze_time("2023-01-15")
class TestPricelistCacheWithDates(TestPricelistCacheHistoryCommonCase):
    def test_cached_price_by_date(self):
        date_start = date(year=2023, month=1, day=1)
        product_id = self.product.id
        pricelist = self.list
        pricelist_id = pricelist.id
        cache_model = self.cache_model
        product_qty_partner = [(self.product, 1, False)]
        # For each day of January, compare the price with what odoo
        # would return
        for days in range(31):
            at_date = date_start + timedelta(days=days)
            cache = cache_model._get_cached_prices(
                pricelist_id, [product_id], at_date=at_date
            )
            odoo_vals = pricelist._compute_price_rule(product_qty_partner, at_date)
            odoo_price = odoo_vals[product_id][0]
            self.assertEqual(cache.price, odoo_price)

    def test_retrieve_base_price(self):
        # the base price is the price unaltered by items.
        # with default implementation in pricelist_cache, the base price is
        # computed as the price of today, even if altered by an item.
        # I.E.
        #  cache is computed the 15th of Jan. Base price is considered as the
        #  price of this day -> 6.0
        #  Therefore, trying to retrieve prices before or after January should fail,
        #  returning 6.0 instead of 320.0
        january_date = date(year=2023, month=1, day=15)
        pricelist = self.ending_list
        product = self.product
        product_qty_partner = [(product, 1, False)]
        cache = self.cache_model._get_cached_prices(
            pricelist.id, product.ids, at_date=january_date
        )
        odoo_vals = pricelist._compute_price_rule(product_qty_partner, january_date)
        odoo_price = odoo_vals[product.id][0]
        self.assertEqual(cache.price, odoo_price)
        # Now, try to retrieve prices ouside or this pricelist dates
        # (2023-01-01 and 2023-01-31)
        # First case, 1 day before price change is effective
        december_date = date(year=2022, month=12, day=31)
        cache = self.cache_model._get_cached_prices(
            pricelist.id, product.ids, at_date=december_date
        )
        odoo_vals = pricelist._compute_price_rule(product_qty_partner, december_date)
        odoo_price = odoo_vals[product.id][0]
        self.assertEqual(cache.price, odoo_price)
        # Second case, 1 day after price change is over
        february_date = date(year=2023, month=2, day=1)
        cache = self.cache_model._get_cached_prices(
            pricelist.id, product.ids, at_date=february_date
        )
        odoo_vals = pricelist._compute_price_rule(product_qty_partner, february_date)
        odoo_price = odoo_vals[product.id][0]
        self.assertEqual(cache.price, odoo_price)

    def test_retrieve_surcharged_price(self):
        # TODO failing,
        # see ./test_pricelist_item_utility_methods.py
        date_start = date(year=2023, month=1, day=1)
        product_id = self.product.id
        pricelist = self.formula_list
        pricelist_id = pricelist.id
        cache_model = self.cache_model
        product_qty_partner = [(self.product, 1, False)]
        # For each day of January, compare the price with what odoo
        # would return
        for days in range(31):
            at_date = date_start + timedelta(days=days)
            cache = cache_model._get_cached_prices(
                pricelist_id, [product_id], at_date=at_date
            )
            odoo_vals = pricelist._compute_price_rule(product_qty_partner, at_date)
            odoo_price = odoo_vals[product_id][0]
            self.assertEqual(cache.price, odoo_price)

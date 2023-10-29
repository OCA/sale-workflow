# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date, timedelta

from freezegun import freeze_time

from .common import TestPricelistCacheHistoryCommonCase


@freeze_time("2023-01-15")
class TestPricelistCacheWithDates(TestPricelistCacheHistoryCommonCase):

    def assert_price_equal(self, pricelist, product, at_date):
        product_qty_partner = [(product, 1, False)]
        cache = self.cache_model.get_cached_prices_for_pricelist(
            pricelist, product, at_date=at_date
        )
        odoo_vals = pricelist._compute_price_rule(product_qty_partner, at_date)
        odoo_price = odoo_vals[product.id][0]
        self.assertEqual(cache.price, odoo_price)

    def test_cached_price_by_date(self):
        date_start = date(year=2023, month=1, day=1)
        product = self.product
        pricelist = self.list
        # For each day of January, compare the price with what odoo
        # would return
        for days in range(31):
            at_date = date_start + timedelta(days=days)
            self.assert_price_equal(pricelist, product, at_date)

    def test_retrieve_base_price(self):
        # the base price is the price unaltered by items.
        # with default implementation in pricelist_cache, the base price is
        # computed as the price of today, even if altered by an item.
        # I.E.
        #  cache is computed the 15th of Jan. Base price is considered as the
        #  price of this day -> 6.0
        #  Therefore, trying to retrieve prices before or after January should fail,
        #  returning 6.0 instead of 320.0
        pricelist = self.ending_list
        products = self.products
        dates = [
            date(year=2022, month=12, day=15),
            date(year=2023, month=1, day=15),
            date(year=2023, month=2, day=15),
            date(year=2023, month=3, day=15),
            date(year=2023, month=4, day=5),
        ]
        for _date in dates:
            for product in products:
                self.assert_price_equal(pricelist, product, _date)

    def test_retrieve_surcharged_price(self):
        # see ./test_pricelist_item_utility_methods.py
        date_start = date(year=2023, month=1, day=1)
        product = self.product
        pricelist = self.formula_list
        cache_model = self.cache_model
        product_qty_partner = [(self.product, 1, False)]
        # For each day of January, compare the price with what odoo
        # would return
        for days in range(31):
            at_date = date_start + timedelta(days=days)
            self.assert_price_equal(pricelist, product, at_date)

    def test_retrieve_surcharged_price_from_factor_list(self):
        date_start = date(year=2023, month=1, day=1)
        product = self.product
        pricelist = self.factor_list
        for days in range(31):
            at_date = date_start + timedelta(days=days)
            self.assert_price_equal(pricelist, product, at_date)

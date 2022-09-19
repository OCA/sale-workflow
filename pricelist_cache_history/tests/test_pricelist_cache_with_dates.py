# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time

from odoo.addons.pricelist_cache.tests.common import TestPricelistCacheCommon

LIST_PRICES_MAPPING = [
    # item1 ongoing until 2021-01-01
    ("pricelist_cache_history.list_with_dates", "2020-12-24", 120.0),
    # item1 and item25 are overlapping. item with the biggers date_end has priority.
    # We should have the price of item25 here.
    ("pricelist_cache_history.list_with_dates", "2021-12-25", 60.0),
    # item25 from 2020-12-25 to 2021-02-20
    ("pricelist_cache_history.list_with_dates", "2021-01-02", 60.0),
    ("pricelist_cache_history.list_with_dates", "2021-02-14", 60.0),
    # item25 and item3 are overlapping. item with the biggest date_end has priority.
    # We should have the price of item3 from 2022-02-15
    ("pricelist_cache_history.list_with_dates", "2021-02-15", 80.0),
    # item3 from 2021-02-15 to 2021-02-28
    ("pricelist_cache_history.list_with_dates", "2021-02-28", 80.0),
    # No item at this date, price fetched from list0 (100.0)
    ("pricelist_cache_history.list_with_dates", "2021-03-01", 100.0),
    ("pricelist_cache_history.list_with_dates", "2021-03-31", 100.0),
    # item4 ongoing from 2021-04-01
    ("pricelist_cache_history.list_with_dates", "2021-04-01", 140.0),
]


@freeze_time("2021-03-15")
class TestPricelistCacheWithDates(TestPricelistCacheCommon):
    def test_whatever(self):
        cache_model = self.env["product.pricelist.cache"].with_context(WITH_TESTS=True)
        for xmlid, date, expected_price in LIST_PRICES_MAPPING:
            pricelist = self.env.ref(xmlid)
            cache_item = cache_model.get_cached_prices_for_pricelist(
                pricelist, self.p6, at_date=date
            )
            self.assertEqual(len(cache_item), 1)
            self.assertEqual(cache_item.price, expected_price)

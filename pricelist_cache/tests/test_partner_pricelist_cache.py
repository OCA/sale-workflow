# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.exceptions import UserError

from .common import LIST_PRICES_MAPPING, TestPricelistCacheCommon


@freeze_time("2021-03-15")
class TestPricelistCache(TestPricelistCacheCommon):
    def test_partner_pricelists(self):
        partner = self.partner
        for pricelist_xmlid, expected_result in LIST_PRICES_MAPPING.items():
            partner.property_product_pricelist = self.env.ref(pricelist_xmlid)
            price_list = partner._pricelist_cache_get_prices()
            # for test purposes, only test products referenced in demo data
            # Since cache is created for more or less products, depending
            # on the modules installed
            price_list = price_list.filtered(lambda p: p.product_id in self.products)
            result = [{"id": c.product_id.id, "price": c.price} for c in price_list]
            result.sort(key=lambda r: r["id"])
            self.assertEqual(result, expected_result)

    def assert_partner_cache_not_available(self):
        regex = r"Pricelist caching in progress. Retry later"
        with self.assertRaisesRegex(UserError, regex):
            self.partner._pricelist_cache_get_prices()

    def assert_partner_cache_available(self):
        self.partner._pricelist_cache_get_prices()

    def test_partner_inconsistent_cache(self):
        # Initialize
        partner = self.partner
        list3 = self.list3
        list2 = self.list2
        list1 = self.list1
        list0 = self.list0
        all_lists = list0 | list1 | list2 | list3
        partner.property_product_pricelist = list3

        # ### No pricelist cached
        # - all_lists computed -> False
        # - all_lists available -> False
        self._flush_cache()
        self.assert_cache_not_available(all_lists)
        self.assert_cache_not_computed(all_lists)
        self.assert_partner_cache_not_available()

        # ### list2 cached
        # Availability
        # - all_lists -> False
        # Computation
        # - list0, list1, list3 -> False
        # - list2               -> True
        self._update_cache(pricelist_ids=list2.ids)
        self.assert_cache_computed(list2)
        self.assert_cache_not_computed(list3 | list1 | list0)
        # No cache is available, because list2 depends on pricelists that
        # haven't been cached.
        self.assert_cache_not_available(all_lists)
        # Therefore, trying to get prices for partner should raise an exception
        self.assert_partner_cache_not_available()

        # ### list1 and list2 cached
        # Availability
        # - all_lists -> False
        # Computation
        # - list0, list3 -> False
        # - list1, list2 -> True
        self._update_cache(pricelist_ids=list1.ids)
        self.assert_cache_computed(list2 | list1)
        self.assert_cache_not_computed(list3 | list0)
        # No cache is available, because list1 and list2 depends on list0 that
        # haven't been cached.
        self.assert_cache_not_available(all_lists)
        # Therefore, trying to get prices for partner should raise an exception
        self.assert_partner_cache_not_available()

        # ### list0, list1, list2 cached
        # Availability
        # - list0, list1, list2 -> True
        # - list3               -> False
        # Computation
        # - list0, list1, list2 -> True
        # - list3               -> False
        self._update_cache(pricelist_ids=list0.ids)
        self.assert_cache_computed(list0 | list1 | list2)
        self.assert_cache_not_computed(list3)
        # Now, all list0-2 are available, because none of them have a parent pricelist
        # that isn't cached
        self.assert_cache_available(list0 | list1 | list2)
        # But list3 itself isnt cached
        self.assert_cache_not_available(list3)
        # And partner cache still cannot be retrieved
        self.assert_partner_cache_not_available()

        # ### All lists cached
        # Availability
        # - all_lists -> True
        # Computation
        # - all_lists -> True
        self._update_cache(pricelist_ids=list3.ids)
        self.assert_cache_available(all_lists)
        self.assert_cache_computed(all_lists)
        self.assert_partner_cache_available()

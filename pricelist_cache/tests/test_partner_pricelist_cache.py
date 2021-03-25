# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

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

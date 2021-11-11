# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import contextlib
import json

from werkzeug.exceptions import Unauthorized

from odoo.addons.pricelist_cache.tests.common import TestPricelistCacheCommon
from odoo.addons.website.tools import MockRequest

from ..controllers.main import PricelistController

LIST_PRICES_MAPPING = {
    "pricelist_cache.list0": [
        {"id": 17, "price": 100.0},
        {"id": 18, "price": 79.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list1": [
        {"id": 17, "price": 75.0},
        {"id": 18, "price": 79.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list2": [
        {"id": 17, "price": 75.0},
        {"id": 18, "price": 79.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list3": [
        {"id": 17, "price": 25.0},
        {"id": 18, "price": 79.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list4": [
        {"id": 17, "price": 15.0},
        {"id": 18, "price": 50.0},
        {"id": 19, "price": 100.0},
        {"id": 20, "price": 47.0},
    ],
    "pricelist_cache.list5": [
        {"id": 17, "price": 45.0},
        {"id": 18, "price": 99.0},
        {"id": 19, "price": 120.0},
        {"id": 20, "price": 67.0},
    ],
}


class TestPricelistCache(TestPricelistCacheCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api_key = cls.env.ref("pricelist_cache_rest.api_key_demo")
        cls.api_key2 = cls.env.ref("pricelist_cache_rest.api_key_demo_2")
        cls.env.company.pricelist_cache_auhorize_apikey_ids += cls.api_key
        cls.ctrl = PricelistController()
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.partner.property_product_pricelist = cls.list0

    @contextlib.contextmanager
    def _get_mocked_request(self, httprequest=None, extra_headers=None):
        with MockRequest(self.env) as mocked_request:
            mocked_request.httprequest = httprequest or mocked_request.httprequest
            headers = {}
            headers.update(extra_headers or {})
            mocked_request.httprequest.headers = headers
            mocked_request.auth_api_key_id = self.api_key.id
            mocked_request.make_response = lambda data, **kw: data
            yield mocked_request

    def test_api_key_validation(self):
        with self._get_mocked_request() as req:
            req.auth_api_key_id = None
            with self.assertRaisesRegex(Unauthorized, "API key missing"):
                self.ctrl.partner_pricelist(self.partner)
        with self._get_mocked_request() as req:
            req.auth_api_key_id = self.api_key2.id
            with self.assertRaisesRegex(Unauthorized, "API key not valid"):
                self.ctrl.partner_pricelist(self.partner)

    def _resp_data(self, resp):
        return json.loads(resp.data.decode())

    def test_get_prices(self):
        partner = self.partner
        for pricelist_xmlid, expected_result in LIST_PRICES_MAPPING.items():
            partner.property_product_pricelist = self.env.ref(pricelist_xmlid)
            result = []
            with self._get_mocked_request():
                resp = self.ctrl.partner_pricelist(partner)
                data = self._resp_data(resp)
                [result.append(c) for c in data if c["id"] in self.products.ids]
                self.assertEqual(result, expected_result)

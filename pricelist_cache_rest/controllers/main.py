# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json

from werkzeug.exceptions import Unauthorized

from odoo import http


class PricelistController(http.Controller):
    """Expose prices for pricelists."""

    @http.route(
        "/pricelist/<model('res.partner'):partner>",
        type="http",
        auth="api_key",
        methods=["GET"],
        csrf=False,
    )
    def partner_pricelist(self, partner):
        """Retrive all prices for given partner.

        :return: TODO
        """
        env = http.request.env
        auth_api_key_id = getattr(http.request, "auth_api_key_id", None)
        self._validate_api_key(env, auth_api_key_id)

        cache_items = self._get_cache_items(partner)
        return self._make_json_response(self._cache_to_json(cache_items))

    def _validate_api_key(self, env, api_key_id):
        if api_key_id is None:
            raise Unauthorized("API key missing")
        allowed_keys = self._get_authorized_api_keys(env)
        if api_key_id not in allowed_keys:
            raise Unauthorized("API key not valid")
        return True

    def _get_authorized_api_keys(self, env):
        # TODO: what about multi company support?
        return env.company.pricelist_cache_auhorize_apikey_ids.ids

    def _get_cache_items(self, partner):
        return partner._pricelist_cache_get_prices()

    def _make_json_response(self, data):
        headers = {}
        headers["Content-Type"] = "application/json"
        return http.request.make_response(json.dumps(data), headers=headers)

    def _cache_to_json(self, cache_items):
        exporter = cache_items.env.ref("pricelist_cache_rest.ir_exp_cache_item")
        return cache_items.jsonify(exporter.get_json_parser())

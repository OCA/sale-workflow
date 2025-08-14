# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.http import request
from odoo.osv import expression

from odoo.addons.portal.controllers import portal


class CustomerPortalSaleOrderSearch(portal.CustomerPortal):
    def _get_searchbar_order_inputs(self):
        return {
            "all": {"label": _("All"), "input": "all"},
            "name": {"label": _("Order Ref"), "input": "name"},
            "ref": {"label": _("Order Customer Ref"), "input": "ref"},
            "partner": {"label": _("Customer"), "input": "partner"},
        }

    def _get_search_order_domain(self, search):
        search_in = request.params.get("search_in", "all")
        search_domain = []
        if search_in == "all":
            search_domain = expression.OR(
                [
                    [("name", "ilike", search)],
                    [("client_order_ref", "ilike", search)],
                    [("partner_id.name", "ilike", search)],
                ]
            )
        elif search_in == "name":
            search_domain = [("name", "ilike", search)]
        elif search_in == "ref":
            search_domain = [("client_order_ref", "ilike", search)]
        elif search_in == "partner":
            search_domain = [("partner_id.name", "ilike", search)]
        return search_domain

    def _prepare_quotations_domain(self, partner):
        domain = super()._prepare_quotations_domain(partner)
        search = request.params.get("search", "").strip()
        if search:
            search_domain = self._get_search_order_domain(search)
            domain = expression.AND([domain, search_domain])
        return domain

    def _prepare_orders_domain(self, partner):
        domain = super()._prepare_orders_domain(partner)
        search = request.params.get("search", "").strip()
        if search:
            search_domain = self._get_search_order_domain(search)
            domain = expression.AND([domain, search_domain])
        return domain

    def _prepare_sale_portal_rendering_values(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        quotation_page=False,
        **kwargs,
    ):
        values = super()._prepare_sale_portal_rendering_values(
            page=page,
            date_begin=date_begin,
            date_end=date_end,
            sortby=sortby,
            quotation_page=quotation_page,
            **kwargs,
        )
        search = request.params.get("search") or ""
        search_in = request.params.get("search_in") or "all"
        values.update(
            {
                "search": search,
                "search_in": search_in,
                "searchbar_inputs": self._get_searchbar_order_inputs(),
            }
        )
        return values

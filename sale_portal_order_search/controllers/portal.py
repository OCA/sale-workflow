# Copyright 2023 Tecnativa - Carlos Roca
# Copyright 2023 Trey Kilobytes de Soluciones SL - Antonio Ruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.http import route

from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortal(CustomerPortal):
    def get_sale_order_domain(self, response, kw, name):
        return [
            ('id', 'in', response.qcontext[name].ids),
            ('name', 'ilike', kw['search'])
        ]

    @route()
    def portal_my_orders(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        """Inject search term in the context so it can be used in the search
        method in sale.order to filter orders from the portal"""
        response = super().portal_my_orders(
            page=page,
            date_begin=date_begin,
            date_end=date_end,
            sortby=sortby,
            **kw,
        )
        name = 'orders'
        if "search" in kw:
            domain = self.get_sale_order_domain(response, kw, name)
            orders = response.qcontext[name].search(domain)
            response.qcontext[name] = orders
        response.qcontext.setdefault("searchbar_inputs", {})
        label_search = _("Search in Sales & Orders")
        pager = portal_pager(
            url="/my/orders",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "search": kw.get("search"),
                "search_in": "portal_order_filter",
            },
            total=len(response.qcontext.get('orders', 0)),
            page=page,
            step=self._items_per_page,
        )
        response.qcontext["searchbar_inputs"].update(
            {
                "portal_order_filter": {
                    "input": "portal_order_filter",
                    "label": label_search,
                },
            }
        )
        response.qcontext["pager"] = pager
        response.qcontext["search_in"] = "portal_order_filter"
        return response

    @route()
    def portal_my_quotes(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        """Inject search term in the context so it can be used in the search
        method in sale.order to filter quotes from the portal"""
        response = super().portal_my_quotes(
            page=page,
            date_begin=date_begin,
            date_end=date_end,
            sortby=sortby,
            **kw,
        )
        name = 'quotations'
        if "search" in kw:
            domain = self.get_sale_order_domain(response, kw, name)
            orders = response.qcontext[name].search(domain)
            response.qcontext[name] = orders
        response.qcontext.setdefault("searchbar_inputs", {})
        label_search = _("Search in Sales Quotations")
        pager = portal_pager(
            url="/my/quotes",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "search": kw.get("search"),
                "search_in": "portal_quotations_filter",
            },
            total=len(response.qcontext.get('quotations', 0)),
            page=page,
            step=self._items_per_page,
        )
        response.qcontext["searchbar_inputs"].update(
            {
                "portal_quotations_filter": {
                    "input": "portal_quotations_filter",
                    "label": label_search,
                },
            }
        )
        response.qcontext["pager"] = pager
        response.qcontext["search_in"] = "portal_quotations_filter"
        return response

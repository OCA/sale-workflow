# Copyright 2023 Tecnativa - Carlos Roca
# Copyright 2023 Trey Kilobytes de Soluciones SL - Antonio Ruz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_portal_search_domain(self, portal_order_filter):
        return (
            "|",
            ("name", "ilike", portal_order_filter),
            ("ref", "ilike", portal_order_filter),
        )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Display only standalone contact matching ``args`` or having
        attached contact matching ``args``"""
        portal_order_filter = self.env.context.get("portal_order_filter")
        if portal_order_filter:
            portal_search_domain = self._get_portal_search_domain(
                portal_order_filter)
            args = expression.AND([args, portal_search_domain])
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )

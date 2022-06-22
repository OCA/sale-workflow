# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        # Reorder so that other checkings (ie. sale_tier_validation) are done
        # before updating fields.
        result = super(SaleOrder, self).action_confirm()
        address_fields = ["partner_shipping_id", "partner_invoice_id"]
        cache = {}
        for order in self:
            for field in address_fields:
                order[field] = self._get_cached_partner(order[field], cache)
        return result

    def _get_cached_partner(self, partner, cache):
        copied_partner = cache.get(partner)
        if not copied_partner:
            copied_partner = partner.sudo()._version_create()
            cache[partner] = copied_partner
        return copied_partner

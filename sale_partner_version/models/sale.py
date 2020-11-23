# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        address_fields = ["partner_shipping_id", "partner_invoice_id"]
        for order in self:
            for field in address_fields:
                order[field] = order[field]._version_create()
        return super(SaleOrder, self).action_confirm()

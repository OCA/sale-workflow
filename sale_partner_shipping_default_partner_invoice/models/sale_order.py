# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_id", "partner_shipping_id")
    def _compute_partner_invoice_id(self):
        orders = self.filtered(
            lambda o: o.partner_shipping_id.default_partner_invoice_id
        )
        for order in orders:
            order.partner_invoice_id = (
                order.partner_shipping_id.default_partner_invoice_id
            )
        return super(SaleOrder, self - orders)._compute_partner_invoice_id()

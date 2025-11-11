# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Add compute method to the standard field
    carrier_id = fields.Many2one(
        compute="_compute_carrier_id",
        store=True,
        readonly=False,
    )

    @api.depends("partner_shipping_id")
    def _compute_carrier_id(self):
        for order in self:
            order.carrier_id = False
            if order.partner_shipping_id.property_delivery_carrier_id:
                order.carrier_id = (
                    order.partner_shipping_id.property_delivery_carrier_id
                )

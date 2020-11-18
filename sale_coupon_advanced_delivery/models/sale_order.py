# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    """Extend to make promotions recompute aware of delivery lines."""

    _inherit = "sale.order"

    def get_update_pricelist_order_lines(self):
        """Extend to ignore delivery lines."""
        order_lines = super().get_update_pricelist_order_lines()
        return order_lines.filtered(lambda r: not r.is_delivery)

    def recompute_coupon_lines(self):
        """Extend to trigger delivery price update."""
        super().recompute_coupon_lines()
        ChooseDeliveryCarrier = self.env["choose.delivery.carrier"]
        for order in self.filtered(lambda r: r.carrier_id):
            choose_delivery_carrier = ChooseDeliveryCarrier.create(
                {"order_id": order.id, "carrier_id": order.carrier_id.id}
            )
            choose_delivery_carrier.update_price()
            choose_delivery_carrier.button_confirm()

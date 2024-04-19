# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def action_confirm(self):
        self._add_delivery_carrier_on_confirmation()
        return super().action_confirm()

    def _add_delivery_carrier_on_confirmation(self):
        """Automatically add delivery.carrier on sale order confirmation"""
        for order in self:
            if (
                not order.company_id.carrier_auto_assign
                or order.delivery_set
                or order.is_all_service
            ):
                continue
            order._set_delivery_carrier_on_confirm()

    # Migration note 17.0: merge with same method from delivery_auto_refresh
    # and rename to _set_delivery_carrier
    def _set_delivery_carrier_on_confirm(self, set_delivery_line=True):
        for order in self:
            delivery_wiz_action = order.action_open_delivery_wizard()
            delivery_wiz_context = delivery_wiz_action.get("context", {})
            if not delivery_wiz_context.get("default_carrier_id"):
                continue
            delivery_wiz = (
                self.env[delivery_wiz_action.get("res_model")]
                .with_context(**delivery_wiz_context)
                .new({})
            )

            # Do not override carrier
            if order.carrier_id:
                delivery_wiz.carrier_id = order.carrier_id

            # If the carrier isn't allowed, we won't default to it
            if (
                delivery_wiz.carrier_id
                not in delivery_wiz.available_carrier_ids._origin
            ):
                continue

            if not set_delivery_line or order.is_all_service:
                # Only set the carrier
                if order.carrier_id != delivery_wiz.carrier_id:
                    order.carrier_id = delivery_wiz.carrier_id
            else:
                delivery_wiz._get_shipment_rate()
                delivery_wiz.button_confirm()

# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _set_delivery_carrier(self, set_delivery_line=True):
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
                return

            if not set_delivery_line or order.is_all_service:
                # Only set the carrier
                if order.carrier_id != delivery_wiz.carrier_id:
                    order.carrier_id = delivery_wiz.carrier_id
            else:
                delivery_wiz._get_shipment_rate()
                delivery_wiz.button_confirm()

    @api.onchange("partner_id", "partner_shipping_id")
    def _add_delivery_carrier_on_partner_change(self):
        partner = self.partner_shipping_id or self.partner_id
        if not partner:
            return
        if self.company_id.carrier_auto_assign_on_create:
            self._set_delivery_carrier(set_delivery_line=False)

    def _is_auto_set_carrier_on_create(self):
        self.ensure_one()
        if self.state not in ("draft", "sent"):
            return False
        if self.company_id.carrier_auto_assign_on_create:
            return True
        return False

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if not order.carrier_id and order._is_auto_set_carrier_on_create():
                order._set_delivery_carrier()
        return orders

    def _add_delivery_carrier_on_confirmation(self):
        """Automatically add delivery.carrier on sale order confirmation"""
        for order in self:
            if order.delivery_set:
                continue
            if order.is_all_service:
                continue
            order._set_delivery_carrier()

    def action_confirm(self):
        for order in self:
            if not order.company_id.carrier_auto_assign_on_confirm:
                continue
            order._add_delivery_carrier_on_confirmation()
        return super().action_confirm()

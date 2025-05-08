# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("partner_id", "partner_shipping_id")
    def _add_delivery_carrier_on_partner_change(self):
        partner = self.partner_shipping_id or self.partner_id
        if not partner:
            return
        if self.company_id.carrier_on_create:
            self._set_delivery_carrier(
                set_delivery_line=False,
                preserve_order_carrier=False,
            )

    def _is_auto_set_carrier_on_create(self):
        self.ensure_one()
        return (
            self.state in ("draft", "sent")
            and self.company_id.carrier_on_create
            and not self.is_all_service
        )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if not order.carrier_id and order._is_auto_set_carrier_on_create():
                order._set_delivery_carrier()
        return orders

    def _is_auto_set_carrier_on_confirm(self):
        self.ensure_one()
        return self.company_id.carrier_auto_assign and not self.is_all_service

    def action_confirm(self):
        for order in self:
            if order._is_auto_set_carrier_on_confirm():
                order._set_delivery_carrier(
                    set_delivery_line=True,
                    preserve_order_carrier=True,
                )
        return super().action_confirm()

    def _set_delivery_carrier(
        self, set_delivery_line=True, preserve_order_carrier=True
    ):
        """Automatically change delivery carrier.

        :param set_delivery_line: It will create or update the delivery line
        :param preserve_order_carrier: It will respect the carrier set on the order
        """
        for order in self:
            if order.delivery_set:
                continue
            delivery_wiz_action = order.action_open_delivery_wizard()
            delivery_wiz_context = delivery_wiz_action.get("context", {})
            if not delivery_wiz_context.get("default_carrier_id"):
                continue
            delivery_wiz_model = self.env[
                delivery_wiz_action.get("res_model")
            ].with_context(**delivery_wiz_context)
            if self._origin:
                delivery_wiz = delivery_wiz_model.create({})
            else:
                delivery_wiz = delivery_wiz_model.new({})
            # Do not override carrier
            if preserve_order_carrier and order.carrier_id:
                delivery_wiz.carrier_id = order.carrier_id
            if not set_delivery_line or order.is_all_service:
                # Only set the carrier
                if order.carrier_id != delivery_wiz.carrier_id:
                    order.carrier_id = delivery_wiz.carrier_id
            else:
                delivery_wiz._get_delivery_rate()
                delivery_wiz.button_confirm()

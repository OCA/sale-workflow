# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _is_auto_set_carrier_on_create(self):
        return (
            not self.carrier_id
            and self.state in ("draft", "sent")
            and self.company_id.carrier_on_create
            and not self.is_all_service
        )

    def _auto_set_carrier_on_create(self):
        if self.env.context.get("carrier_on_create"):
            return
        for rec in self:
            if rec._is_auto_set_carrier_on_create():
                rec.with_context(carrier_on_create=True)._set_delivery_carrier()

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs._auto_set_carrier_on_create()
        return recs

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec._is_auto_set_carrier_on_write(vals):
                rec._set_delivery_carrier(preserve_order_carrier=False)
        return res

    def _is_auto_set_carrier_on_write(self, vals):
        return self.state in ("draft", "sent") and bool(
            not vals.get("carrier_id")
            and (vals.get("partner_id") or vals.get("partner_shipping_id"))
        )

    def _is_auto_set_carrier_on_confirm(self):
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
            if (
                not order.order_line
                or isinstance(order.id, models.NewId)
                and not order._origin
            ):
                continue
            # Preserve the carrier only if explicitly set on the attribute
            if preserve_order_carrier and order.delivery_set:
                continue
            delivery_wiz_action = order.action_open_delivery_wizard()
            delivery_wiz_context = delivery_wiz_action.get("context", {})
            if not delivery_wiz_context.get("default_carrier_id"):
                continue

            delivery_wiz_model = self.env[
                delivery_wiz_action.get("res_model")
            ].with_context(**delivery_wiz_context)

            delivery_wiz = delivery_wiz_model.new({})
            delivery_wiz.order_id = order
            if not delivery_wiz.order_id and order._origin:
                delivery_wiz.order_id = order._origin

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

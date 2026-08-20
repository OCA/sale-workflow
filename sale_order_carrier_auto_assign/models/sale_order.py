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
                order._set_delivery_carrier(set_delivery_line=False)
        return orders

    def _set_carrier_on_create(self):
        if self.env.context.get("carrier_on_create"):
            return
        for order in self:
            if not order.carrier_id and order._is_auto_set_carrier_on_create():
                order.with_context(carrier_on_create=True)._set_delivery_carrier()

    def write(self, vals):
        # When product lines are added, set the carrier
        res = super(SaleOrder, self.with_context(carrier_on_create=True)).write(vals)
        self._set_carrier_on_create()
        return res

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
        for order in self:
            if not order.order_line:
                continue
            # Preserve the carrier only if explicitly set on the attribute
            if preserve_order_carrier and order.delivery_set:
                continue
            if preserve_order_carrier and order.carrier_id:
                carrier = order.carrier_id
            else:
                order = order.with_company(order.company_id)
                ship_partner = order.partner_shipping_id
                carrier_property = (
                    ship_partner.property_delivery_carrier_id
                    or ship_partner.commercial_partner_id.property_delivery_carrier_id
                )
                carrier = carrier_property.available_carriers(ship_partner, order)
                order.carrier_id = carrier

            if set_delivery_line and not order.is_all_service and carrier:
                result = carrier.rate_shipment(order)
                if result.get("success"):
                    price_unit = result["price"]
                    order._create_delivery_line(carrier, price_unit)

    def _prepare_delivery_line_vals(self, carrier, price_unit):
        values = super()._prepare_delivery_line_vals(carrier, price_unit)
        # Set product_uom_id to prevent this field from being recomputed.
        # remove this method when this PR is merged.
        # https://github.com/odoo/odoo/pull/283551
        values["product_uom_id"] = carrier.product_id.uom_id.id
        return values

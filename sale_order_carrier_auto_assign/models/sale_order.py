# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def action_confirm(self):
        for rec in self:
            if not rec.company_id.carrier_auto_assign:
                continue
            rec._add_delivery_carrier_on_confirmation()
        return super().action_confirm()

    def _add_delivery_carrier_on_confirmation(self):
        """Automatically add delivery.carrier on sale order confirmation"""
        for order in self:
            if order.delivery_set:
                continue
            delivery_wiz_action = order.action_open_delivery_wizard()
            delivery_wiz_context = delivery_wiz_action.get("context", {})
            if not delivery_wiz_context.get("default_carrier_id"):
                continue
            delivery_wiz = (
                self.env[delivery_wiz_action.get("res_model")]
                .with_context(**delivery_wiz_context)
                .create({})
            )
            delivery_wiz._get_shipment_rate()
            delivery_wiz.button_confirm()

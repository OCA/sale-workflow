# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.fields import first


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_shipping_id")
    def _compute_warehouse_id(self):
        ret_vals = super()._compute_warehouse_id()
        warehouses = self.env["stock.warehouse"].search(
            [("company_id", "in", [False] + self.company_id.ids)]
        )
        for order in self:
            if not (order.partner_shipping_id and order.state in ["draft", "sent"]):
                continue
            available_warehouse = first(
                warehouses.filtered(
                    lambda wh: wh.company_id.id in [False, order.company_id.id]
                ).warehouses_by_country_state(order.partner_shipping_id)
            )
            if available_warehouse and order.warehouse_id != available_warehouse:
                order.warehouse_id = available_warehouse
        return ret_vals

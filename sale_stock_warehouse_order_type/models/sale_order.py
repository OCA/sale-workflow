# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("type_id")
    def onchange_type_id(self):
        """
        The order to apply default warehouse in a sale order is
        1 - Shipping address
        2 - Partner address
        3 - Sales Person
        4 - Sale order type setting
        The inherit method already checks if the sale order type has not warehouse.
        """
        res = super(SaleOrder, self).onchange_type_id()
        for order in self:
            order_type = order.type_id
            vals = {}
            if order.partner_shipping_id.sale_warehouse_id:
                vals.update(
                    {"warehouse_id": order.partner_shipping_id.sale_warehouse_id.id}
                )
            elif order.partner_id.sale_warehouse_id:
                vals.update({"warehouse_id": order.partner_id.sale_warehouse_id.id})
            elif order.user_id.property_warehouse_id:
                vals.update({"warehouse_id": order.user_id.property_warehouse_id.id})
            elif order_type.warehouse_id:
                vals.update({"warehouse_id": order_type.warehouse_id.id})
            if vals:
                order.update(vals)
        return res

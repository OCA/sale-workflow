# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("type_id")
    def onchange_type_id(self):
        super().onchange_type_id()
        for order in self:
            order_type = order.type_id
            line_vals = {}
            line_vals.update({"route_id": order_type.route_id.id})
            order.order_line.update(line_vals)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.order_id.type_id.route_id:
            self.update({"route_id": self.order_id.type_id.route_id})
        return res

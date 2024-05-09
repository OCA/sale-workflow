# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "container.deposit.order.line.mixin"]

    def _get_product_qty_field(self):
        return "product_uom_qty"

    def _get_product_qty_delivered_received_field(self):
        return "qty_delivered"

    def _get_protected_fields(self):
        protected_fields = super()._get_protected_fields()
        if self.env.context.get("update_order_container_deposit_quantity", False):
            protected_fields.remove("product_uom_qty")
        return protected_fields

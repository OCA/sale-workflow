# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        if self._origin and (
            self.product_uom_qty != self._origin.product_uom_qty
            and self.product_uom == self._origin.product_uom
        ):
            return
        return super().product_uom_change()

# Copyright 2024 Akretion - Clément Mombereau
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        original_price_unit = self.price_unit
        super().product_uom_change()
        if original_price_unit and not self.price_unit:
            self.price_unit = original_price_unit

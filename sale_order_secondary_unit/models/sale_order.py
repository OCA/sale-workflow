# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.secondary.unit.mixin"]
    _name = "sale.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }

    secondary_uom_unit_price = fields.Float(
        string="2nd unit price",
        digits="Product Price",
        compute="_compute_secondary_uom_unit_price",
    )

    product_uom_qty = fields.Float(copy=True)

    @api.depends(
        "display_type",
        "product_id",
        "product_packaging_qty",
        "secondary_uom_qty",
        "secondary_uom_id",
        "product_uom_qty",
    )
    def _compute_product_uom_qty(self):
        res = super()._compute_product_uom_qty()
        for line in self:
            line._compute_helper_target_field_qty()
        return res

    @api.depends("product_id")
    def _compute_product_uom(self):
        res = super()._compute_product_uom()
        for line in self:
            line._onchange_helper_product_uom_for_secondary()
        return res

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super()._onchange_product_id_warning()
        if self.product_id:
            self.secondary_uom_id = self.product_id.sale_secondary_uom_id
            if self.product_uom_qty == 1.0:
                self.secondary_uom_qty = 1.0
                self._onchange_helper_product_uom_for_secondary()
        return res

    @api.depends("secondary_uom_qty", "product_uom_qty", "price_unit")
    def _compute_secondary_uom_unit_price(self):
        for line in self:
            if line.secondary_uom_id:
                try:
                    line.secondary_uom_unit_price = (
                        line.price_subtotal / line.secondary_uom_qty
                    )
                except ZeroDivisionError:
                    line.secondary_uom_unit_price = 0
            else:
                line.secondary_uom_unit_price = 0

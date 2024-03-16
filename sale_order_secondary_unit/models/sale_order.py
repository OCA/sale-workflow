# Copyright 2018-2020 Tecnativa - Carlos Dauden
# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.secondary.unit.mixin"]
    _name = "sale.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }

    secondary_uom_price_unit = fields.Float(
        string="Secondary Unit Price",
        digits="Product Price",
        compute="_compute_secondary_uom_price_unit",
        store=True,
        precompute=True,
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_uom_qty(self):
        res = super()._compute_product_uom_qty()
        self._compute_helper_target_field_qty()
        return res

    @api.onchange("product_uom")
    def _onchange_product_uom(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange("product_id")
    def _onchange_product_id(self):
        inherited_secondary_uom_id = (
            self.product_id.sale_secondary_uom_id
            or self.product_id.product_tmpl_id.sale_secondary_uom_id
        )
        if inherited_secondary_uom_id:
            line_uom_qty = self.product_uom_qty
            self.secondary_uom_id = inherited_secondary_uom_id
            self.product_uom_qty = line_uom_qty

    @api.depends("secondary_uom_qty", "product_uom_qty", "price_subtotal")
    def _compute_secondary_uom_price_unit(self):
        for line in self:
            if line.secondary_uom_id:
                try:
                    line.secondary_uom_price_unit = (
                        line.price_subtotal / line.secondary_uom_qty
                    )
                except ZeroDivisionError:
                    line.secondary_uom_price_unit = 0
            else:
                line.secondary_uom_price_unit = 0

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

    # Inherited fields
    product_uom_qty = fields.Float(
        compute="_compute_product_uom_qty",
        precompute=True,
        store=True,
    )
    secondary_uom_qty = fields.Float(
        compute="_compute_secondary_uom_qty",
        precompute=True,
        store=True,
    )

    @api.depends(
        "display_type",
        "product_id",
        "product_packaging_qty",
        "secondary_uom_qty",
        "secondary_uom_id",
        "product_uom_qty",
    )
    def _compute_product_uom_qty(self):
        self._compute_helper_target_field_qty()
        return super()._compute_product_uom_qty()

    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        """
        If default sales secondary unit set on product, put on secondary
        quantity 1 for being the default quantity. We override this method,
        that is the one that sets by default 1 on the other quantity with that
        purpose.
        """
        res = super()._onchange_product_id_warning()
        line_uom_qty = self.product_uom_qty
        self.secondary_uom_id = self.product_id.sale_secondary_uom_id
        if self.product_id.sale_secondary_uom_id:
            if line_uom_qty == 1.0:
                self.secondary_uom_qty = 1.0
                self.onchange_product_uom_for_secondary()
            else:
                self.product_uom_qty = line_uom_qty
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

# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.secondary.unit.mixin"]
    _name = "sale.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom_id",
    }

    secondary_uom_unit_price = fields.Float(
        string="2nd unit price",
        digits="Product Price",
        compute="_compute_secondary_uom_unit_price",
    )

    product_uom_qty = fields.Float(copy=True)

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_uom_qty(self):
        res = super()._compute_product_uom_qty()
        for line in self:
            line._compute_helper_target_field_qty()
        return res

    def _compute_product_uom_id(self):
        res = super()._compute_product_uom_id()
        for line in self:
            line._onchange_helper_product_uom_for_secondary()
        return res

    @api.onchange("product_id")
    def _onchange_product_id_secondary_uom(self):
        if self.product_id and not self.env.context.get("skip_secondary_uom_default"):
            # Read the quantity before setting the secondary unit: that write
            # schedules _compute_product_uom_qty, which would derive it from a
            # still empty secondary_uom_qty and leave the line at 0.
            product_uom_qty = self.product_uom_qty
            self.secondary_uom_id = self.product_id.sale_secondary_uom_id
            if self.secondary_uom_id:
                self.product_uom_qty = product_uom_qty
                if self.secondary_uom_id.dependency_type != "independent":
                    self._onchange_helper_product_uom_for_secondary()
                elif product_uom_qty == 1.0:
                    # Nothing derives an independent secondary quantity, so a
                    # line left at the default quantity gets one secondary unit.
                    self.secondary_uom_qty = 1.0
                # The secondary quantity is rounded, so recomputing the line
                # quantity back from it would drift away from what was asked.
                self.env.remove_to_compute(self._fields["product_uom_qty"], self)

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

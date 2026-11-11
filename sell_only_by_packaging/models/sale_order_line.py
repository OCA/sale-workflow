# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains(
        "product_id", "product_packaging_id", "product_packaging_qty", "product_uom_qty"
    )
    def _check_product_packaging_sell_only_by_packaging(self):
        for line in self:
            if not line.product_id.sell_only_by_packaging or not line.product_uom_qty:
                continue
            if not line.product_packaging_id:
                raise ValidationError(
                    _(
                        "Please select a packaging for product %s. "
                        "This product can only be sold by packaging.",
                        line.product_id.name,
                    )
                )
            if (
                float_compare(
                    line.product_packaging_qty,
                    int(line.product_packaging_qty),
                    precision_digits=2,
                )
                != 0
            ):
                raise ValidationError(
                    _(
                        "The quantity of product %s must be a multiple of "
                        "the selected packaging quantity.",
                        line.product_id.name,
                    )
                )

    def _force_qty_with_package(self):
        self.ensure_one()
        old_qty = self.product_uom_qty
        qty = self.product_id._convert_packaging_qty(
            self.product_uom_qty,
            self.product_uom,
            packaging=self.product_packaging_id,
        )
        if self.product_packaging_id and qty != old_qty:
            self.product_packaging_qty = self.product_packaging_id._compute_qty(
                qty, self.product_uom
            )
        self.product_uom_qty = qty
        return True

    @api.onchange("product_uom_qty", "product_packaging_id")
    def _onchange_product_uom_qty(self):
        self._force_qty_with_package()

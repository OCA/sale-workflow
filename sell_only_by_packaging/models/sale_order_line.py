# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains(
        "product_id", "product_packaging_id", "product_packaging_qty", "product_uom_qty"
    )
    def _check_product_packaging_sell_only_by_packaging(self):
        errors = []
        for line in self:
            if not line.product_uom_qty:
                continue
            if not line.product_id.sell_only_by_packaging:
                continue
            if error_message_min_qty := line._check_min_qty_packaging():
                errors.append(error_message_min_qty)
        if errors:
            raise ValidationError(
                self.env._(
                    "The following lines has some issues with "
                    + "packaging quantities:\n    - %s",
                    "\n    - ".join(errors),
                )
            )

    def _check_min_qty_packaging(self):
        if (
            not self.product_packaging_id
            or float_compare(
                self.product_packaging_qty,
                int(self.product_packaging_qty),
                precision_digits=2,
            )
            != 0
        ):
            return self.env._(
                "Product %s can only be sold with a packaging and a "
                "packaging quantity.",
                self.product_id.name,
            )

    def _force_qty_with_package(self):
        self.ensure_one()
        qty = self.product_id._convert_packaging_qty(
            self.product_uom_qty, self.product_uom, packaging=self.product_packaging_id
        )
        self.product_uom_qty = qty
        return True

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty(self):
        self._force_qty_with_package()

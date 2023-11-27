# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from math import ceil

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

            if (
                not line.product_packaging_id
                or float_compare(
                    line.product_packaging_qty,
                    int(line.product_packaging_qty),
                    precision_digits=2,
                )
                != 0
            ):
                raise ValidationError(
                    _(
                        "Product %s can only be sold with a packaging and a "
                        "packaging quantity."
                    )
                    % line.product_id.name
                )

    def _force_qty_with_package(self):
        """

        :return:
        """
        self.ensure_one()
        qty = self.product_id._convert_packaging_qty(
            self.product_uom_qty, self.product_uom, packaging=self.product_packaging_id
        )
        self.product_uom_qty = qty
        return True

    @api.onchange("product_packaging_id")
    def _onchange_product_packaging_id(self):
        # Round up to the next integer and avoid the Warning raised by
        # _onchange_product_packaging_id defined in the sale addon
        ceiled_product_packaging_qty = ceil(self.product_packaging_qty)
        self.product_packaging_qty = ceiled_product_packaging_qty or 1
        return super()._onchange_product_packaging_id()

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty(self):
        self._force_qty_with_package()

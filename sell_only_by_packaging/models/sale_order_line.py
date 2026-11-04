# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id")
    def _compute_product_uom_id(self):
        """Default to the smallest packaging unit of the product.

        Without this, the line would default to the product unit, which is
        never an acceptable unit for a product sold only by packaging.
        """
        res = super()._compute_product_uom_id()
        for line in self:
            if not line.product_id.sell_only_by_packaging:
                continue
            if line.product_uom_id in line.product_id.uom_ids:
                continue
            line.product_uom_id = (
                line.product_id._get_min_sellable_uom() or line.product_uom_id
            )
        return res

    @api.constrains("product_id", "product_uom_id", "product_uom_qty")
    def _check_product_packaging_sell_only_by_packaging(self):
        for line in self:
            if not line.product_id.sell_only_by_packaging or not line.product_uom_qty:
                continue

            if (
                line.product_uom_id not in line.product_id.uom_ids
                or float_compare(
                    line.product_uom_qty,
                    int(line.product_uom_qty),
                    precision_digits=2,
                )
                != 0
            ):
                raise ValidationError(
                    self.env._(
                        "Product %s can only be sold in a packaging unit, with a "
                        "whole number of packagings as quantity.",
                        line.product_id.name,
                    ),
                )

    def _force_qty_with_package(self):
        self.ensure_one()
        self.product_uom_qty = self.product_id._convert_packaging_qty(
            self.product_uom_qty, self.product_uom_id
        )
        return True

    @api.onchange("product_uom_qty", "product_uom_id")
    def _onchange_sell_only_by_packaging_qty(self):
        self._force_qty_with_package()

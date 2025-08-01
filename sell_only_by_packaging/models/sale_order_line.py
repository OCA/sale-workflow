# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round


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
            if error_message_qty_multiple := line._check_pkg_qty_multiple():
                errors.append(error_message_qty_multiple)
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

    def _check_pkg_qty_multiple(self):
        # Ported from sale_stock.models.sale_order_line,_check_package on v14
        default_uom = self.product_id.uom_id
        pack = self.product_packaging_id
        qty = self.product_uom_qty
        q = default_uom._compute_quantity(pack.qty, self.product_uom)
        # We do not use the modulo operator to check if qty is a multiple of q.
        # Indeed the qty per package might be a float, leading to incorrect results.
        # For example: 8 % 1.6 = 1.5999999999999996
        #              5.4 % 1.8 = 2.220446049250313e-16
        if (
            qty
            and q
            and float_compare(
                qty / q,
                float_round(qty / q, precision_rounding=1.0),
                precision_rounding=0.001,
            )
            != 0
        ):
            next_valid_qty = qty - (qty % q) + q
            return self.env._(
                "This product is packaged by %(pack_size).2f %(pack_name)s. "
                + "You should sell %(quantity).2f %(unit)s.",
                pack_size=pack.qty,
                pack_name=default_uom.name,
                quantity=next_valid_qty,
                unit=self.product_uom.name,
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

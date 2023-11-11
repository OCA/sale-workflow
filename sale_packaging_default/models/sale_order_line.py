# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id", "product_uom_qty", "product_uom")
    def _compute_product_packaging_id(self):
        """Set a default packaging for sales if possible."""
        for line in self:
            if line.product_id and not line.product_packaging_id:
                line.product_packaging_id = (
                    line.product_id.packaging_ids.filtered_domain(
                        [("sales_default", "=", True), ("sales", "=", True)]
                    )[:1]
                )
        return super()._compute_product_packaging_id()

    @api.depends("product_packaging_id", "product_uom", "product_uom_qty")
    def _compute_product_packaging_qty(self):
        """Set a valid packaging quantity."""
        result = super()._compute_product_packaging_qty()
        for line in self:
            if not line.product_packaging_id:
                continue
            # Reset to 1 packaging if it's empty or not a whole number
            if not line.product_packaging_qty or line.product_packaging_qty % 1:
                line.product_packaging_qty = 1
        return result

    @api.depends(
        "display_type",
        "product_id",
        "product_packaging_id",
        "product_packaging_qty",
    )
    def _compute_product_uom_qty(self):
        # Avoid a circular dependency. Upstream `product_uom_qty` has an
        # undeclared dependency over `product_packaging_qty`, which depends
        # again on `product_uom_qty`.
        _self = self.with_context(keep_product_packaging=True)
        return super(SaleOrderLine, _self)._compute_product_uom_qty()

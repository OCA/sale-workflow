# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from contextlib import suppress

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def onchange(self, values, field_name, field_onchange):
        """Record which field was being changed."""
        if isinstance(field_name, list):
            names = set(field_name)
        elif field_name:
            names = {field_name}
        else:
            names = set()
        _self = self.with_context(changing_fields=names)
        return super(SaleOrderLine, _self).onchange(values, field_name, field_onchange)

    @api.depends("product_id", "product_uom_qty", "product_uom")
    def _compute_product_packaging_id(self):
        """Set a default packaging for sales if possible."""
        if not self.env.context.get("apply_default_packaging", True):
            return super()._compute_product_packaging_id()

        for line in self:
            if line.product_id != line.product_packaging_id.product_id:
                line.product_packaging_id = line._get_default_packaging(line.product_id)
        result = super()._compute_product_packaging_id()
        # If there's no way to package the desired qty, remove the packaging.
        # It is only done when the user is currently manually setting
        # `product_uom_qty` to zero. In other cases, we are maybe getting
        # default values and this difference will get fixed by other compute
        # methods later.
        if (
            self.env.context.get("changing_fields")
            and "product_uom_qty" not in self.env.context["changing_fields"]
        ):
            return result
        for line in self:
            with suppress(ZeroDivisionError):
                if (
                    line.product_uom_qty
                    and line.product_uom_qty % line.product_packaging_id.qty
                ):
                    line.product_packaging_id = False
        return result

    @api.model
    def _get_default_packaging(self, product):
        return fields.first(
            product.packaging_ids.filtered_domain([("sales", "=", True)])
        )

    @api.depends("product_packaging_id", "product_uom", "product_uom_qty")
    def _compute_product_packaging_qty(self):
        """Set a valid packaging quantity."""
        changing_fields = self.env.context.get("changing_fields", set())
        # Keep the packaging qty when changing the product
        if "product_id" in changing_fields and all(
            line.product_id and line.product_packaging_qty for line in self
        ):
            return
        result = super()._compute_product_packaging_qty()
        for line in self:
            if not line.product_packaging_id:
                continue
            # Reset to 1 packaging if it's empty or not a whole number
            if not line.product_packaging_qty or line.product_packaging_qty % 1:
                line.product_packaging_qty = int(
                    "product_uom_qty" not in changing_fields
                )
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
        result = super(SaleOrderLine, _self)._compute_product_uom_qty()
        return result

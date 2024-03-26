# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    product_packaging = fields.Many2one(ondelete="restrict")

    def _can_be_sold_error_condition(self):
        self.ensure_one()
        return self.product_packaging and not self.product_packaging.can_be_sold

    @api.constrains("product_packaging")
    def _check_product_packaging_can_be_sold(self):
        for line in self:
            if line._can_be_sold_error_condition():
                raise ValidationError(
                    _(
                        "Packaging %s on product %s must be set as 'Can be sold'"
                        " in order to be used on a sale order."
                    )
                    % (line.product_packaging.name, line.product_id.name)
                )

    @api.onchange("product_packaging")
    def _onchange_product_packaging(self):
        if self._can_be_sold_error_condition():
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "This product packaging must be set as 'Can be sold' in"
                        " order to be used on a sale order."
                    ),
                },
            }
        return super()._onchange_product_packaging()

    @api.constrains(
        "product_id", "product_packaging", "product_packaging_qty", "product_uom_qty"
    )
    def _check_product_packaging_sell_only_by_packaging(self):
        for line in self:
            if not line.product_id.sell_only_by_packaging:
                continue
            if (
                not line.product_packaging
                or float_compare(
                    line.product_packaging_qty,
                    0,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                <= 0
            ):
                raise ValidationError(
                    _(
                        "Product %s can only be sold with a packaging and a "
                        "packaging qantity." % line.product_id.name
                    )
                )

    def _force_qty_with_package(self):
        """

        :return:
        """
        self.ensure_one()
        qty = self.product_id._convert_packaging_qty(
            self.product_uom_qty, self.product_uom, packaging=self.product_packaging
        )
        self.product_uom_qty = qty
        return True

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty(self):
        self._force_qty_with_package()
        res = super()._onchange_product_uom_qty()
        return res

    def _get_product_packaging_having_multiple_qty(self, product, qty, uom):
        if uom != product.uom_id:
            qty = uom._compute_quantity(qty, product.uom_id)
        return product.get_first_packaging_with_multiple_qty(qty)

    def _inverse_product_packaging_qty(self):
        # Force skipping of auto assign
        # if we are writing the product_uom_qty directly via inverse
        super(
            SaleOrderLine, self.with_context(_skip_auto_assign=True)
        )._inverse_product_packaging_qty()

    def _inverse_qty_delivered(self):
        # Force skipping of auto assign
        super(
            SaleOrderLine, self.with_context(_skip_auto_assign=True)
        )._inverse_qty_delivered()

    def write(self, vals):
        """Auto assign packaging if needed"""
        if "product_packaging" in vals.keys() or self.env.context.get(
            "_skip_auto_assign"
        ):
            # setting the packaging directly, skip auto assign
            return super().write(vals)
        for line in self:
            line_vals = vals.copy()
            line_vals.update(line._write_auto_assign_packaging(line_vals))
            super(SaleOrderLine, line).write(line_vals)
        return True

    def _write_auto_assign_packaging(self, vals):
        self.ensure_one()
        product = (
            self.env["product.product"].browse(vals["product_id"])
            if "product_id" in vals
            else self.product_id
        )
        if product:
            quantity = (
                vals["product_uom_qty"]
                if "product_uom_qty" in vals
                else self.product_uom_qty
            )
            uom = (
                self.env["uom.uom"].browse(vals["product_uom"])
                if "product_uom" in vals
                else self.product_uom
            )
            # Here, we ensure that no package is already set on the line.
            # If so, it could lead to errors, since product_packaging_qty
            # isn't updated after product_packaging has been modified.
            # The simple way to handle that is to not modify product_packaging
            # if one is already set.
            if not self.product_packaging:
                packaging = self._get_product_packaging_having_multiple_qty(
                    product, quantity, uom
                )
                if packaging:
                    return {"product_packaging": packaging.id}
            # No need to raise an error here if no packaging has been found
            #  since the error on _check_product_packaging will be raised
        return {}

    @api.model
    def create(self, vals):
        """Auto assign packaging if needed"""
        # Fill the packaging if they are empty and the quantity is a multiple
        if not vals.get("product_packaging"):
            vals.update(self._create_auto_assign_packaging(vals))
        return super().create(vals)

    @api.model
    def _create_auto_assign_packaging(self, vals):
        product = (
            self.env["product.product"].browse(vals["product_id"])
            if "product_id" in vals
            else False
        )
        if product and product.sell_only_by_packaging:
            quantity = vals.get("product_uom_qty")
            uom = self.env["uom.uom"].browse(vals.get("product_uom"))
            packaging = self._get_product_packaging_having_multiple_qty(
                product, quantity, uom
            )
            if packaging:
                return {"product_packaging": packaging.id}
            # No need to raise an error here if no packaging has been found
            #  since the error on _check_product_packaging will be raised
        return {}

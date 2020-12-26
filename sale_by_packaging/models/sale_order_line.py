# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

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

    @api.constrains("product_id", "product_packaging")
    def _check_product_packaging_sell_only_by_packaging(self):
        for line in self:
            if line.product_id.sell_only_by_packaging and not line.product_packaging:
                raise ValidationError(
                    _(
                        "Product %s can only be sold with a packaging."
                        % line.product_id.name
                    )
                )

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id.sell_only_by_packaging:
            first_packaging = fields.first(
                self.product_id.packaging_ids.filtered(
                    lambda p: not float_is_zero(
                        p.qty, precision_rounding=p.product_uom_id.rounding
                    )
                )
            )
            if first_packaging:
                self.update(
                    {
                        "product_packaging": first_packaging.id,
                        "product_uom_qty": first_packaging.qty,
                    }
                )
        return res

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
        if not res:
            res = self._check_qty_is_pack_multiple()
        return res

    def _check_qty_is_pack_multiple(self):
        """ Check only for product with sell_only_by_packaging
        """
        # and we dont want to have this warning when we had the product
        if self.product_id.sell_only_by_packaging:
            if not self._get_product_packaging_having_multiple_qty(
                self.product_id, self.product_uom_qty, self.product_uom
            ):
                warning_msg = {
                    "title": _("Product quantity cannot be packed"),
                    "message": _(
                        "For the product {prod}\n"
                        "The {qty} is not the multiple of any pack.\n"
                        "Please add a package"
                    ).format(prod=self.product_id.name, qty=self.product_uom_qty),
                }
                return {"warning": warning_msg}
        return {}

    def _get_product_packaging_having_multiple_qty(self, product, qty, uom):
        if uom != product.uom_id:
            qty = uom._compute_quantity(qty, product.uom_id)
        return product.get_first_packaging_with_multiple_qty(qty)

    def write(self, vals):
        """Auto assign packaging if needed"""
        fields_to_check = ["product_id", "product_uom_qty", "product_uom"]
        if vals.get("product_packaging") or not any(
            fname in vals for fname in fields_to_check
        ):
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
        if product and product.sell_only_by_packaging:
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

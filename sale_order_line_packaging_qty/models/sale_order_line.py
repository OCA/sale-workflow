# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    product_packaging_qty = fields.Float(
        string="Package quantity",
        compute="_compute_product_packaging_qty",
        inverse="_inverse_product_packaging_qty",
        digits="Product Unit of Measure",
    )

    @api.depends(
        "product_uom_qty", "product_uom", "product_packaging", "product_packaging.qty"
    )
    def _compute_product_packaging_qty(self):
        for sol in self:
            if (
                not sol.product_packaging
                or sol.product_uom_qty == 0
                or sol.product_packaging.qty == 0
            ):
                sol.product_packaging_qty = 0
                continue
            # Consider uom
            if sol.product_id.uom_id != sol.product_uom:
                product_qty = sol.product_uom._compute_quantity(
                    sol.product_uom_qty, sol.product_id.uom_id
                )
            else:
                product_qty = sol.product_uom_qty
            sol.product_packaging_qty = product_qty / sol.product_packaging.qty

    def _prepare_product_packaging_qty_values(self):
        self.ensure_one()
        return {
            "product_uom_qty": self.product_packaging.qty * self.product_packaging_qty,
            "product_uom": self.product_packaging.product_uom_id.id,
        }

    def _inverse_product_packaging_qty(self):
        for sol in self:
            if sol.product_packaging_qty and not sol.product_packaging:
                raise UserError(
                    _(
                        "You must define a package before setting a quantity "
                        "of said package."
                    )
                )
            if sol.product_packaging and sol.product_packaging.qty == 0:
                raise UserError(
                    _("Please select a packaging with a quantity bigger than 0")
                )
            if sol.product_packaging and sol.product_packaging_qty:
                sol.write(sol._prepare_product_packaging_qty_values())

    @api.onchange("product_packaging_qty")
    def _onchange_product_packaging_qty(self):
        if self.product_packaging and self.product_packaging_qty:
            self.update(self._prepare_product_packaging_qty_values())

    @api.onchange("product_packaging")
    def _onchange_product_packaging(self):
        if self.product_packaging:
            self.update(
                {
                    "product_packaging_qty": 1,
                    "product_uom_qty": self.product_packaging.qty,
                    "product_uom": self.product_id.uom_id,
                }
            )
        else:
            self.update({"product_packaging_qty": 0})
        return super()._onchange_product_packaging()

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty(self):
        """
        Ensure a warning is raised when changing the package if the qty
        is not a multiple of the package qty.
        """
        # TODO Drop once https://github.com/odoo/odoo/pull/49150/ is merged
        res = super()._onchange_product_uom_qty()
        if not res:
            res = self._check_package() or self._check_qty_is_pack_multiple()
        return res

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id.sell_only_by_packaging:
            self.product_uom_qty = min(self.product_id.packaging_ids.mapped("qty"))
        return res

    def _check_qty_is_pack_multiple(self):
        """ Check only for product with sell_only_by_packaging
        """
        # and we dont want to have this warning when we had the product
        if self.product_id.sell_only_by_packaging:
            if not self._is_pack_multiple():
                warning_msg = {
                    "title": _("Product quantity can not be packed"),
                    "message": _(
                        "For the product {prod}\n"
                        "The {qty} is not the multiple of any pack.\n"
                        "Please add a package"
                    ).format(prod=self.product_id.name, qty=self.product_uom_qty),
                }
                return {"warning": warning_msg}
        return {}

    def _is_pack_multiple(self):
        return bool(self.product_id._which_pack_multiple(self.product_uom_qty))

    def write(self, vals):
        # Fill the packaging if they are empty and the quantity is a multiple
        for line in self:
            product_uom_qty = vals.get("product_uom_qty")
            product_packaging = vals.get("product_packaging")
            if line.product_id.sell_only_by_packaging and (
                not line.product_packaging
                or ("product_packaging" in vals and not product_packaging)
            ):
                pack_multiple = line.product_id._which_pack_multiple(product_uom_qty)
                if pack_multiple:
                    vals.update({"product_packaging": pack_multiple.id})
        return super().write(vals)

    @api.model
    def create(self, vals):

        # Fill the packaging if they are empty and the quantity is a multiple
        product = self.env["product.product"].browse(vals.get("product_id"))
        product_uom_qty = vals.get("product_uom_qty")
        product_packaging = vals.get("product_packaging")

        if product and product.sell_only_by_packaging and not product_packaging:
            pack_multiple = product._which_pack_multiple(product_uom_qty)
            if pack_multiple:
                vals.update({"product_packaging": pack_multiple.id})
        return super().create(vals)

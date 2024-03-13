from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _can_be_sold_error_condition(self):
        self.ensure_one()
        return self.product_packaging_id and not self.product_packaging_id.can_be_sold

    @api.constrains("product_packaging_id")
    def _check_product_packaging_can_be_sold(self):
        for line in self:
            if line._can_be_sold_error_condition():
                raise ValidationError(
                    _(
                        f"Packaging {line.product_packaging_id.name} on "
                        f"product {line.product_id.name} must be set as 'Can be sold'"
                        f" in order to be used on a sale order."
                    )
                    % (line.product_packaging_id.name, line.product_id.name)
                )

    @api.onchange("product_id", "order_partner_id")
    def _onchange_product_id_warning(self):
        self.product_packaging_id = False
        self._force_packaging()
        self._force_qty_with_package()
        return super(SaleOrderLine, self)._onchange_product_id_warning()

    def _get_product_packaging_having_multiple_qty(self, product, qty, uom):
        if uom != product.uom_id:
            qty = uom._compute_quantity(qty, product.uom_id)
        return product.get_first_packaging_with_multiple_qty(qty)

    def _get_autoassigned_packaging(self, vals=None):
        if not vals:
            vals = []
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
                return packaging.id
        return None

    def _force_packaging(self):
        if not self.product_packaging_id and self.product_id.sell_only_by_packaging:
            packaging_id = self._get_autoassigned_packaging()
            if packaging_id:
                self.update({"product_packaging_id": packaging_id})

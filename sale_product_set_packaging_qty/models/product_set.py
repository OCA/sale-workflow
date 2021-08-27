# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    product_packaging_id = fields.Many2one(
        "product.packaging", domain="[('product_id', '=', product_id)]"
    )
    product_packaging_qty = fields.Float(
        compute="_compute_product_packaging_qty",
        inverse="_inverse_product_packaging_qty",
        digits="Product Unit of Measure",
    )

    @api.depends("quantity", "product_packaging_id", "product_packaging_id.qty")
    def _compute_product_packaging_qty(self):
        for line in self:
            uom_rounding = line.product_id.uom_id.rounding
            if (
                not line.product_packaging_id
                or float_is_zero(line.quantity, precision_rounding=uom_rounding)
                or float_is_zero(
                    line.product_packaging_id.qty, precision_rounding=uom_rounding
                )
            ):
                line.product_packaging_qty = 0
                continue
            line.product_packaging_qty = line.quantity / line.product_packaging_id.qty

    def _inverse_product_packaging_qty(self):
        for line in self:
            if line.product_packaging_qty and not line.product_packaging_id:
                raise UserError(
                    _(
                        "You must define a package before setting a quantity "
                        "of said package."
                    )
                )
            if line.product_packaging_id and line.product_packaging_id.qty == 0:
                raise UserError(
                    _("Please select a packaging with a quantity bigger than 0")
                )
            if line.product_packaging_id and line.product_packaging_qty:
                line.write(line._prepare_product_packaging_qty_values())

    def _prepare_product_packaging_qty_values(self):
        self.ensure_one()
        return {
            "quantity": self.product_packaging_id.qty * self.product_packaging_qty,
        }

    @api.onchange("product_packaging_qty")
    def _onchange_product_packaging_qty(self):
        if self.product_packaging_id and self.product_packaging_qty:
            self.update(self._prepare_product_packaging_qty_values())

    @api.onchange("product_packaging_id")
    def _onchange_product_packaging(self):
        if self.product_packaging_id:
            self.update(
                {"product_packaging_qty": 1, "quantity": self.product_packaging_id.qty}
            )
        else:
            self.update({"product_packaging_qty": 0})

    def prepare_sale_order_line_values(self, order, quantity, max_sequence=0):
        res = super().prepare_sale_order_line_values(
            order, quantity, max_sequence=max_sequence
        )
        if self.product_packaging_id:
            res["product_packaging"] = self.product_packaging_id.id
        return res

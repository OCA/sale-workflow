# Copyright 2026 Eshan Desle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrderLineKitComponent(models.Model):
    _name = "sale.order.line.kit.component"
    _description = "Sale Order Line Kit Component"
    _order = "sequence, id"

    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Order Line",
        required=True,
        ondelete="cascade",
        index=True,
    )
    bom_line_id = fields.Many2one(
        comodel_name="mrp.bom.line",
        string="BoM Line",
        ondelete="set null",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain="[('type', '=', 'consu')]",
        required=True,
    )
    product_qty = fields.Float(
        string="Quantity",
        digits="Product Unit of Measure",
        default=1.0,
        required=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        required=True,
    )
    is_selected = fields.Boolean(
        string="Selected",
        default=True,
    )
    sequence = fields.Integer(
        default=10,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="sale_line_id.company_id",
        store=True,
        readonly=True,
    )

    @api.constrains("product_qty")
    def _check_product_qty(self):
        for comp in self:
            if comp.product_qty < 0:
                raise ValidationError(
                    self.env._("Kit component quantity cannot be negative.")
                )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_confirmed_order(self):
        for comp in self:
            if comp.sale_line_id.order_id.state in ("sale", "cancel"):
                raise UserError(
                    self.env._(
                        "Cannot delete kit components on a confirmed or cancelled "
                        "sale order."
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("sale_line_id"):
                sale_line = self.env["sale.order.line"].browse(vals["sale_line_id"])
                if sale_line and sale_line.order_id.state in ("sale", "cancel"):
                    raise UserError(
                        self.env._(
                            "Cannot add kit components to a confirmed or cancelled "
                            "sale order."
                        )
                    )
            if not vals.get("product_id") and vals.get("bom_line_id"):
                bom_line = self.env["mrp.bom.line"].browse(vals["bom_line_id"])
                if bom_line.exists():
                    vals["product_id"] = bom_line.product_id.id
                    if not vals.get("product_uom_id"):
                        vals["product_uom_id"] = bom_line.product_uom_id.id
            if vals.get("product_id") and not vals.get("product_uom_id"):
                product = self.env["product.product"].browse(vals["product_id"])
                if product.exists():
                    vals["product_uom_id"] = product.uom_id.id
        return super().create(vals_list)

    def write(self, vals):
        for comp in self:
            if comp.sale_line_id.order_id.state in ("sale", "cancel"):
                raise UserError(
                    self.env._(
                        "Cannot modify kit components on a confirmed or cancelled "
                        "sale order."
                    )
                )
        return super().write(vals)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id

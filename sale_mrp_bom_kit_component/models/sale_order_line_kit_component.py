# Copyright 2026 Eshan Desle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id

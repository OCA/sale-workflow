# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SOMultiWarehouseChangeLineWizard(models.TransientModel):
    _name = "so.multi.warehouse.change.line.wizard"
    _description = "Sale Order Multi Warehouse Change Line Wizard"

    so_multi_warehouse_change_wizard_id = fields.Many2one(
        string="SO Multi Warehouse Change Wizard",
        comodel_name="so.multi.warehouse.change.wizard",
    )
    sale_order_line_warehouse_id = fields.Many2one(
        string="Current Warehouse",
        comodel_name="sale.order.line.warehouse",
        readonly=True,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        related="sale_order_line_warehouse_id.product_id",
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        digits="Product Unit of Measure",
        related="sale_order_line_warehouse_id.product_uom_qty",
    )
    product_uom_id = fields.Many2one(
        string="Unit Of Measure",
        comodel_name="uom.uom",
        related="sale_order_line_warehouse_id.product_uom_id",
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        related="sale_order_line_warehouse_id.warehouse_id",
    )

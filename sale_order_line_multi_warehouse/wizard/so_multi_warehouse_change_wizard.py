# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SOMultiWarehouseChangeWizard(models.TransientModel):
    _name = "so.multi.warehouse.change.wizard"
    _description = "Sale Order Multi Warehouse Change Wizard"

    sale_order_id = fields.Many2one(string="Sale Order", comodel_name="sale.order")
    current_warehouse_id = fields.Many2one(
        string="Current Warehouse",
        comodel_name="stock.warehouse",
        related="sale_order_id.warehouse_id",
    )
    new_warehouse_id = fields.Many2one(
        string="New Warehouse",
        comodel_name="stock.warehouse",
    )
    so_multi_warehouse_change_line_ids = fields.One2many(
        comodel_name="so.multi.warehouse.change.line.wizard",
        compute="_compute_so_multi_warehouse_change_line_ids",
        inverse_name="so_multi_warehouse_change_wizard_id",
    )

    @api.depends("new_warehouse_id")
    def _compute_so_multi_warehouse_change_line_ids(self):
        for sel in self:
            lines = self.env["so.multi.warehouse.change.line.wizard"]
            if sel.new_warehouse_id:
                vals = []
                incompatible_lines = (
                    sel.sale_order_id.get_incompatible_multi_warehouse_lines(
                        sel.new_warehouse_id
                    )
                )
                if incompatible_lines:
                    for incompatible_line in incompatible_lines:
                        vals.append(
                            {"sale_order_line_warehouse_id": incompatible_line.id}
                        )
                    lines = lines.create(vals)
            sel.so_multi_warehouse_change_line_ids = lines

    def change_warehouse(self):
        self.ensure_one()
        if self.sale_order_id.state not in ["sale", "done"] and self.new_warehouse_id:
            for line in self.so_multi_warehouse_change_line_ids:
                so_line_warehouse = line.sale_order_line_warehouse_id
                related_lines = (
                    so_line_warehouse.order_line_id.sale_order_line_warehouse_ids
                )
                same_warehouse_line = related_lines.filtered(
                    lambda a: a.warehouse_id == self.new_warehouse_id
                )
                if same_warehouse_line:
                    same_warehouse_line[0].write(
                        {
                            "product_uom_qty": same_warehouse_line[0].product_uom_qty
                            + line.sale_order_line_warehouse_id.product_uom_qty
                        }
                    )
                    line.sale_order_line_warehouse_id.unlink()
                else:
                    line.sale_order_line_warehouse_id.write(
                        {"warehouse_id": self.new_warehouse_id.id}
                    )
            self.sale_order_id.write({"warehouse_id": self.new_warehouse_id.id})
        else:
            raise ValidationError(
                _(
                    "Warehouse cannot be changed as sale order is in {} state.".format(
                        self.sale_order_id.state
                    )
                )
            )

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
        inverse_name="so_multi_warehouse_change_wizard_id",
    )
    has_incompatibilities = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        copy=False,
    )

    @api.onchange("new_warehouse_id")
    def _onchange_warehouse_id(self):
        self.has_incompatibilities = False

    def check_incompatible(self):
        self.so_multi_warehouse_change_line_ids.unlink()
        for sel in self.filtered("new_warehouse_id"):
            vals = []
            incompatible_lines = (
                sel.sale_order_id.get_incompatible_multi_warehouse_lines(
                    sel.new_warehouse_id
                )
            )
            has_incompatibilities = "no"
            if incompatible_lines:
                has_incompatibilities = "yes"
                for incompatible_line in incompatible_lines:
                    vals.append(
                        {
                            "sale_order_line_warehouse_id": incompatible_line.id,
                            "so_multi_warehouse_change_wizard_id": sel.id,
                        }
                    )
                self.env["so.multi.warehouse.change.line.wizard"].create(vals)
            sel.write({"has_incompatibilities": has_incompatibilities})
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
            "context": self.env.context,
        }

    def change_warehouse(self):
        self.ensure_one()
        if self.sale_order_id.state not in ["sale", "done"] and self.new_warehouse_id:
            for line in self.so_multi_warehouse_change_line_ids:
                so_line_warehouse = line.sale_order_line_warehouse_id
                related_lines = (
                    so_line_warehouse.order_line_id.sale_order_line_warehouse_ids
                )
                same_warehouse_line = fields.first(
                    related_lines.filtered(
                        lambda a: a.warehouse_id == self.new_warehouse_id
                    )
                )
                if same_warehouse_line:
                    same_warehouse_line.write(
                        {
                            "product_uom_qty": same_warehouse_line.product_uom_qty
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
                    "Warehouse cannot be changed as sale order is in %(state)s state.",
                    state=self.sale_order_id.state,
                )
            )

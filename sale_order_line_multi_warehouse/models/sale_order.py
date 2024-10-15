# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    allow_sale_multi_warehouse = fields.Boolean(
        compute="_compute_allow_sale_multi_warehouse", store=True
    )
    suitable_warehouse_ids = fields.Many2many(
        string="Suitable Warehouses",
        comodel_name="stock.warehouse",
        compute="_compute_suitable_warehouse_ids",
    )

    @api.depends("company_id")
    def _compute_allow_sale_multi_warehouse(self):
        for order in self:
            order.allow_sale_multi_warehouse = (
                order.company_id.allow_sale_multi_warehouse
            )

    @api.depends("warehouse_id")
    def _compute_suitable_warehouse_ids(self):
        for order in self:
            order.suitable_warehouse_ids = (
                order.warehouse_id + order.warehouse_id.alternative_warehouse_ids
            )

    def get_incompatible_multi_warehouse_lines(self, warehouse):
        self.ensure_one()
        compatible_warehouse_ids = warehouse + warehouse.alternative_warehouse_ids
        return self.order_line.mapped("sale_order_line_warehouse_ids").filtered(
            lambda a: a.warehouse_id.id not in compatible_warehouse_ids.ids
        )

    def _action_confirm(self):
        for order in self:
            if order.get_incompatible_multi_warehouse_lines(self.warehouse_id):
                raise ValidationError(
                    _(
                        "Some sale order line assignment lines are not compatible with "
                        "the selected warehouse. Quotation {} could not be validated.".format(
                            order.name
                        )
                    )
                )
        return super()._action_confirm()

    def action_open_so_multi_warehouse_change(self):
        self.ensure_one()
        view_id = self.env.ref(
            "sale_order_line_multi_warehouse.so_multi_warehouse_change_wizard_view"
        )
        ctx = {
            "default_sale_order_id": self.id,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "so.multi.warehouse.change.wizard",
            "target": "new",
            "view_id": view_id.id,
            "context": ctx,
        }

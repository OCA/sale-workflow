# Copyright 2026 Eshan Desle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    kit_component_ids = fields.One2many(
        comodel_name="sale.order.line.kit.component",
        inverse_name="sale_line_id",
        string="Kit Components",
        copy=True,
    )
    is_kit = fields.Boolean(
        compute="_compute_is_kit",
        store=True,
        compute_sudo=True,
    )

    @api.depends("product_id", "bom_id")
    def _compute_is_kit(self):
        for line in self:
            if not line.product_id:
                line.is_kit = False
                continue
            bom = line.bom_id or self.env["mrp.bom"]._bom_find(
                line.product_id,
                company_id=line.company_id.id,
                bom_type="phantom",
            ).get(line.product_id)
            line.is_kit = bool(bom and bom.type == "phantom")

    def _get_kit_bom(self):
        self.ensure_one()
        if not self.product_id:
            return self.env["mrp.bom"]
        if self.bom_id and self.bom_id.type == "phantom":
            return self.bom_id
        return (
            self.env["mrp.bom"]
            ._bom_find(
                self.product_id,
                company_id=self.company_id.id,
                bom_type="phantom",
            )
            .get(self.product_id, self.env["mrp.bom"])
        )

    def _populate_kit_components(self):
        for line in self:
            bom = line._get_kit_bom()
            if not bom:
                line.kit_component_ids = [Command.clear()]
                continue
            new_lines = []
            for sequence, bom_line in enumerate(bom.bom_line_ids, start=1):
                if bom_line._skip_bom_line(line.product_id):
                    continue
                new_lines.append(
                    Command.create(
                        {
                            "bom_line_id": bom_line.id,
                            "product_id": bom_line.product_id.id,
                            "product_qty": bom_line.product_qty,
                            "product_uom_id": bom_line.product_uom_id.id,
                            "is_selected": True,
                            "sequence": bom_line.sequence or sequence,
                        }
                    )
                )
            line.kit_component_ids = [Command.clear()] + new_lines

    @api.onchange("product_id", "bom_id")
    def _onchange_kit_bom_populate_components(self):
        for line in self:
            if line.is_kit:
                line._populate_kit_components()
            else:
                line.kit_component_ids = [Command.clear()]

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.is_kit and not line.kit_component_ids:
                line._populate_kit_components()
        return lines

    def write(self, vals):
        if "product_id" in vals and "bom_id" not in vals:
            new_product = self.env["product.product"].browse(vals["product_id"])
            mismatched_lines = self.filtered(
                lambda line: line.bom_id
                and not (
                    (line.bom_id.product_id and line.bom_id.product_id == new_product)
                    or (
                        not line.bom_id.product_id
                        and line.bom_id.product_tmpl_id == new_product.product_tmpl_id
                    )
                )
            )
            if mismatched_lines:
                super(SaleOrderLine, mismatched_lines).write({"bom_id": False})
        res = super().write(vals)
        if "product_id" in vals or "bom_id" in vals:
            if "kit_component_ids" not in vals:
                for line in self:
                    if line.order_id.state not in ("sale", "cancel"):
                        if line.is_kit:
                            line._populate_kit_components()
                        else:
                            line.kit_component_ids = [Command.clear()]
        return res

    def action_reload_kit_components(self):
        for line in self:
            if line.order_id.state in ("sale", "cancel"):
                raise UserError(
                    self.env._(
                        "Cannot reset kit components on a confirmed or cancelled "
                        "sale order."
                    )
                )
            line._populate_kit_components()
        return True

    def action_open_kit_components(self):
        self.ensure_one()
        view_id = self.env.ref(
            "sale_mrp_bom_kit_component.view_sale_order_line_kit_component_form"
        ).id
        return {
            "name": self.env._("Kit Components: %s", self.product_id.display_name),
            "type": "ir.actions.act_window",
            "res_model": "sale.order.line",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "new",
        }

# Copyright 2026 Eshan Desle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
                line.kit_component_ids = [(5, 0, 0)]
                continue
            new_lines = []
            for sequence, bom_line in enumerate(bom.bom_line_ids, start=1):
                new_lines.append(
                    (
                        0,
                        0,
                        {
                            "bom_line_id": bom_line.id,
                            "product_id": bom_line.product_id.id,
                            "product_qty": bom_line.product_qty,
                            "product_uom_id": bom_line.product_uom_id.id,
                            "is_selected": True,
                            "sequence": bom_line.sequence or sequence,
                        },
                    )
                )
            line.kit_component_ids = [(5, 0, 0)] + new_lines

    @api.onchange("product_id", "bom_id")
    def _onchange_kit_bom_populate_components(self):
        for line in self:
            if line.is_kit:
                line._populate_kit_components()
            else:
                line.kit_component_ids = [(5, 0, 0)]

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.is_kit and not line.kit_component_ids:
                line._populate_kit_components()
        return lines

    def action_reload_kit_components(self):
        self._populate_kit_components()
        return True

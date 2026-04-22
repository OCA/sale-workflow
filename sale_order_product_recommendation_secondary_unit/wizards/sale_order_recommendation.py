# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderRecommendation(models.TransientModel):
    _inherit = "sale.order.recommendation"

    def _prepare_recommendation_line_vals(self, group_line, so_line=False):
        vals = super()._prepare_recommendation_line_vals(group_line, so_line=so_line)
        if so_line:
            vals["secondary_uom_id"] = so_line.secondary_uom_id.id
            vals["secondary_uom_qty"] = so_line.secondary_uom_qty
        if not vals.get("secondary_uom_id"):
            # Take default secondary unit from product if exists
            product = self.env["product.product"].browse(vals["product_id"])
            if product.sale_secondary_uom_id:
                vals["secondary_uom_id"] = product.sale_secondary_uom_id.id
        return vals


class SaleOrderRecommendationLine(models.TransientModel):
    _inherit = ["sale.order.recommendation.line", "product.secondary.unit.mixin"]
    _name = "sale.order.recommendation.line"

    _secondary_unit_fields = {
        "qty_field": "units_included",
        "uom_field": "sale_uom_id",
    }
    _product_uom_field = "uom_id"

    secondary_uom_name = fields.Char(
        string="Secondary Unit", related="secondary_uom_id.name"
    )
    product_tmpl_id = fields.Many2one(
        related="product_id.product_tmpl_id",
        readonly=True,
        help="To filter secondary uom available",
    )
    product_uom_readonly = fields.Boolean(related="sale_line_id.product_uom_readonly")
    units_included = fields.Float(
        store=True,
        readonly=False,
        compute="_compute_units_included",
        copy=True,
        precompute=True,
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_units_included(self):
        self._compute_helper_target_field_qty()

    @api.onchange("sale_uom_id")
    def onchange_sale_uom_id_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    def _prepare_update_so_line_vals(self):
        vals = super()._prepare_update_so_line_vals()
        if self.secondary_uom_id:
            # Avoid error when product_uom_readonly is True
            if vals.get("secondary_uom_id", False) != self.secondary_uom_id.id:
                vals["secondary_uom_id"] = self.secondary_uom_id.id
            vals["secondary_uom_qty"] = self.secondary_uom_qty
        return vals

    def _prepare_new_so_line_vals(self, sequence):
        vals = super()._prepare_new_so_line_vals(sequence)
        if self.secondary_uom_id:
            vals["secondary_uom_id"] = self.secondary_uom_id.id
            vals["secondary_uom_qty"] = self.secondary_uom_qty
        return vals

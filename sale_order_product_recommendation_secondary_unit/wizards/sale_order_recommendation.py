# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_round


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
    _inherit = "sale.order.recommendation.line"

    secondary_uom_id = fields.Many2one(comodel_name="product.secondary.unit")
    secondary_uom_name = fields.Char(related="secondary_uom_id.name")
    secondary_uom_qty = fields.Float(
        string="Secondary Qty", digits="Product Unit of Measure"
    )
    product_tmpl_id = fields.Many2one(
        related="product_id.product_tmpl_id",
        readonly=True,
        help="To filter secondary uom available",
    )
    product_uom_readonly = fields.Boolean(related="sale_line_id.product_uom_readonly")

    @api.onchange("secondary_uom_id", "secondary_uom_qty")
    def _onchange_secondary_uom(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_id.uom_id.factor
        qty = float_round(
            self.secondary_uom_qty * factor,
            precision_rounding=self.product_id.uom_id.rounding,
        )
        if (
            float_compare(
                self.units_included,
                qty,
                precision_rounding=self.product_id.uom_id.rounding,
            )
            != 0
        ):
            self.units_included = qty

    @api.onchange("units_included")
    def _onchange_units_included_sale_order_secondary_unit(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_id.uom_id.factor
        qty = float_round(
            self.units_included / (factor or 1.0),
            precision_rounding=self.secondary_uom_id.uom_id.rounding,
        )
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.secondary_uom_id.uom_id.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty

    def _prepare_update_so_line(self, line_form):
        res = super()._prepare_update_so_line(line_form)
        if self.secondary_uom_id:
            # Avoid error when product_uom_readonly is True
            if line_form.secondary_uom_id != self.secondary_uom_id:
                line_form.secondary_uom_id = self.secondary_uom_id
            line_form.secondary_uom_qty = self.secondary_uom_qty
        return res

    def _prepare_new_so_line(self, line_form, sequence):
        res = super()._prepare_new_so_line(line_form, sequence)
        if self.secondary_uom_id:
            line_form.secondary_uom_id = self.secondary_uom_id
            line_form.secondary_uom_qty = self.secondary_uom_qty
        return res

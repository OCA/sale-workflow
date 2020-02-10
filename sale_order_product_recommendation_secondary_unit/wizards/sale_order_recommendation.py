# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_round


class SaleOrderRecommendationLine(models.TransientModel):
    _inherit = "sale.order.recommendation.line"

    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        related="product_id.sale_secondary_uom_id",
    )
    secondary_uom_qty = fields.Float(
        string="Secondary Qty", digits="Product Unit of Measure"
    )
    product_tmpl_id = fields.Many2one(
        related="product_id.product_tmpl_id",
        readonly=True,
        help="To filter secondary uom available",
    )

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

    def _prepare_update_so_line(self):
        res = super()._prepare_update_so_line()
        if self.secondary_uom_id and self.secondary_uom_qty:
            res.update(
                {
                    "secondary_uom_id": self.secondary_uom_id.id,
                    "secondary_uom_qty": self.secondary_uom_qty,
                }
            )
        return res

    def _prepare_new_so_line(self, sequence):
        res = super()._prepare_new_so_line(sequence)
        if self.secondary_uom_id and self.secondary_uom_qty:
            res.update(
                {
                    "secondary_uom_id": self.secondary_uom_id.id,
                    "secondary_uom_qty": self.secondary_uom_qty,
                }
            )
        return res

    def _trigger_so_line_onchanges(self, so_line):
        """We need to recompute secondary uom qty from the units in the line"""
        secondary_uom_id = self.secondary_uom_id
        so_line = super()._trigger_so_line_onchanges(so_line)
        if secondary_uom_id and self.secondary_uom_qty:
            # Prevent product defaults
            if so_line.secondary_uom_id != secondary_uom_id:
                so_line.secondary_uom_id = secondary_uom_id
            so_line.onchange_secondary_unit_product_uom_qty()
        return so_line

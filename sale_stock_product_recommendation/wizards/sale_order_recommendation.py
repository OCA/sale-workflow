# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import api, fields, models

GHOST_LINE_DEPS = (
    "price_unit",
    "product_id",
    "sale_line_id",
    "units_included",
    "wizard_id.order_id",
)


class SaleOrderRecommendationLine(models.TransientModel):
    _inherit = "sale.order.recommendation.line"

    # Fields required by qty_at_date_widget, with hardcoded names
    display_qty_widget = fields.Boolean(compute="_compute_qty_to_deliver")
    forecast_expected_date = fields.Datetime(compute="_compute_qty_at_date")
    free_qty_today = fields.Float(
        compute="_compute_qty_at_date", digits="Product Unit of Measure"
    )
    is_mto = fields.Boolean(compute="_compute_is_mto")
    move_ids = fields.One2many(related="sale_line_id.move_ids")
    product_uom = fields.Many2one(related="sale_line_id.product_uom", string="UoM")
    qty_available_today = fields.Float(compute="_compute_qty_at_date")
    qty_to_deliver = fields.Float(
        compute="_compute_qty_to_deliver", digits="Product Unit of Measure"
    )
    scheduled_date = fields.Datetime(compute="_compute_qty_at_date")
    state = fields.Selection(related="wizard_id.order_id.state")
    virtual_available_at_date = fields.Float(
        compute="_compute_qty_at_date", digits="Product Unit of Measure"
    )
    warehouse_id = fields.Many2one(related="wizard_id.order_id.warehouse_id")

    def _ghost_sale_lines(self):
        """In-memory sale.order.line equivalents to current recommendations."""
        result = self.env["sale.order.line"]
        for line in self:
            result += self.env["sale.order.line"].new(
                {
                    "order_id": line.wizard_id.order_id.id,
                    "price_unit": line.price_unit,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.units_included,
                },
                line.sale_line_id,
            )
        return result

    @api.depends(
        "sale_line_id.display_qty_widget",
        "sale_line_id.qty_delivered",
        *GHOST_LINE_DEPS
    )
    def _compute_qty_to_deliver(self):
        """Compute the visibility of the inventory widget."""
        for line, ghost_line in zip(self, self._ghost_sale_lines(), strict=True):
            line.qty_to_deliver = ghost_line.qty_to_deliver
            line.display_qty_widget = ghost_line.display_qty_widget

    @api.depends(
        "sale_line_id.forecast_expected_date",
        "sale_line_id.free_qty_today",
        "sale_line_id.qty_available_today",
        "sale_line_id.scheduled_date",
        "sale_line_id.virtual_available_at_date",
        *GHOST_LINE_DEPS
    )
    def _compute_qty_at_date(self):
        """Compute the quantity forecasted of product at delivery date."""
        for line, ghost_line in zip(self, self._ghost_sale_lines(), strict=True):
            line.forecast_expected_date = ghost_line.forecast_expected_date
            line.free_qty_today = ghost_line.free_qty_today
            line.qty_available_today = ghost_line.qty_available_today
            line.scheduled_date = ghost_line.scheduled_date
            line.virtual_available_at_date = ghost_line.virtual_available_at_date

    @api.depends("sale_line_id.is_mto", *GHOST_LINE_DEPS)
    def _compute_is_mto(self):
        """Compute if the product is made to order."""
        for line, ghost_line in zip(self, self._ghost_sale_lines(), strict=True):
            line.is_mto = ghost_line.is_mto

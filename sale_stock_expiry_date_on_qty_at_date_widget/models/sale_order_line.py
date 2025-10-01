# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    predicted_first_expiration_date = fields.Date(
        compute="_compute_predicted_first_expiration_date",
        store=False,
    )

    @api.depends("product_id", "product_uom_qty", "warehouse_id")
    def _compute_predicted_first_expiration_date(self):
        self.predicted_first_expiration_date = False
        for record in self:
            if not record.product_id.use_expiration_date:
                continue
            # Get quants in the same order that will be used
            quants = (
                self.env["stock.quant"]
                .sudo()
                ._gather(
                    record.product_id, record.warehouse_id.lot_stock_id, strict=False
                )
            )
            min_expiration_date = None
            remaining_qty = record.product_uom_qty
            for quant in quants:
                if (
                    float_compare(
                        remaining_qty,
                        0.0,
                        precision_rounding=record.product_uom.rounding,
                    )
                    <= 0
                ):
                    # No remaining quantity
                    break
                if (
                    float_compare(
                        quant.available_quantity,
                        0.0,
                        precision_rounding=quant.product_uom_id.rounding,
                    )
                    <= 0
                ):
                    # No available quantity
                    continue
                quant_available_qty_line_uom = quant.product_uom_id._compute_quantity(
                    quant.available_quantity, record.product_uom
                )
                remaining_qty -= quant_available_qty_line_uom  # Quant will be used
                lot_expiration_date = quant.lot_id.expiration_date
                if not lot_expiration_date:
                    continue
                if not min_expiration_date or lot_expiration_date < min_expiration_date:
                    min_expiration_date = lot_expiration_date

            record.predicted_first_expiration_date = min_expiration_date

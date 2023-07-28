# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        res = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        sale_line_id = values.get("sale_line_id", False)
        # Record can be a sale order line or a stock move depending of pull
        # and push rules
        if sale_line_id:
            record = self.env["sale.order.line"].browse(sale_line_id)
        else:
            record = values.get("move_dest_ids", self.env["stock.move"].browse())[:1]
        if record and record.elaboration_ids:
            res.update(
                {
                    "elaboration_ids": [(6, 0, record.elaboration_ids.ids)],
                    "elaboration_note": record.elaboration_note,
                }
            )
        return res

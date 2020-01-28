# Copyright 2019 Tecnativa - Sergio Teruel
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
        if values.get("sale_line_id"):
            sale_line = self.env["sale.order.line"].browse(values["sale_line_id"])
            if sale_line.secondary_uom_id:
                res.update(
                    {
                        "secondary_uom_id": sale_line.secondary_uom_id.id,
                        "secondary_uom_qty": sale_line.secondary_uom_qty,
                    }
                )
        return res

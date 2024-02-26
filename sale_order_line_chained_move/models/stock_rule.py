# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    preserve_separate_so_lines = fields.Boolean(
        default=False,
        string="Preserve Separate Sale Order Lines",
        help="Prevents Odoo's default behaviour of merging moves with the same product.",
    )

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
        res.update({"related_sale_line_id": values.get("related_sale_line_id")})
        return res

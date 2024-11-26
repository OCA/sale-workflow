# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    call_off_sale_line_id = fields.Many2one(
        "sale.order.line", "Call Off Sale Line", index="btree_not_null"
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("call_off_sale_line_id")
        return distinct_fields

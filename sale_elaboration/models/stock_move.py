# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = ["stock.move", "product.elaboration.mixin"]
    _name = "stock.move"

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        """Don't merge moves with distinct elaborations"""
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields += ["elaboration_ids", "elaboration_note"]
        return distinct_fields


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    elaboration_ids = fields.Many2many(related="move_id.elaboration_ids")
    elaboration_note = fields.Char(related="move_id.elaboration_note")

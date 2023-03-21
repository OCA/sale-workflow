# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = ["stock.move", "product.elaboration.mixin"]
    _name = "stock.move"


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    elaboration_ids = fields.Many2many(related="move_id.elaboration_ids")
    elaboration_note = fields.Char(related="move_id.elaboration_note")

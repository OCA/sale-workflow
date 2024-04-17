# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # So we can view it in our Kanban
    sale_order_id = fields.Many2one(related="sale_line_id.order_id")

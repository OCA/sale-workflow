# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    sale_order_line_warehouse_id = fields.Many2one(
        string="Sale Order Line Warehouse", comodel_name="sale.order.line.warehouse"
    )

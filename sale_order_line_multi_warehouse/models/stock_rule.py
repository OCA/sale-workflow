# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        move_fields = super()._get_custom_move_fields()
        move_fields += ["sale_order_line_warehouse_id"]
        return move_fields

# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        for pick in self.filtered(lambda x: x.picking_type_code == "outgoing"):
            elaboration_lines = pick.move_lines.filtered(
                lambda x: x.sale_line_id.elaboration_ids
            )
            for line in elaboration_lines:
                for product in line.sale_line_id.elaboration_ids.product_id:
                    pick.sale_id._create_elaboration_line(product, line.quantity_done)
        return res

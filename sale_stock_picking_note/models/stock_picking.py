# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """
        Inherit to fill the note (on the picking) with value of picking_note on the SO
        """
        values = super()._get_new_picking_values()
        sale_note = self.sale_line_id.order_id.picking_note
        if sale_note:
            values.update({"note": sale_note})
        return values

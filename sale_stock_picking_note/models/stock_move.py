# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        vals = super()._get_new_picking_values()
        sale_note = self.sale_line_id.order_id.picking_note
        if sale_note:
            vals.update({"note": sale_note})
        vals.update({"customer_note": self.sale_line_id.order_id.picking_customer_note})
        return vals

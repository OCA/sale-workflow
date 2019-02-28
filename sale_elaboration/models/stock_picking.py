# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        with self.env.norecompute():
            for pick in self.filtered(
                lambda x: x.picking_type_code == 'outgoing'
            ):
                elaboration_lines = pick.move_lines.filtered(
                    lambda x: x.sale_line_id.elaboration_id
                )
                for line in elaboration_lines:
                    pick.sale_id._create_elaboration_line(
                        line.sale_line_id.elaboration_id.product_id,
                        line.quantity_done,
                    )
        self.recompute()
        return res

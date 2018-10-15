# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from collections import defaultdict


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        elaboration_product = defaultdict(lambda: 0.0)
        for pick in self.filtered(lambda x: x.picking_type_code == 'outgoing'):
            elaboration_lines = pick.move_lines.filtered(
                lambda x: (
                    x.sale_line_id.elaboration_id and
                    x.sale_line_id.elaboration_id.product_id
                ))
            for line in elaboration_lines:
                product = line.sale_line_id.elaboration_id.product_id
                elaboration_product[product] += line.quantity_done
            for product, qty in elaboration_product.items():
                pick.sale_id._create_elaboration_line(product, qty)
        return res

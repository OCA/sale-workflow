# -*- coding: utf-8 -*-
# © 2015 Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class procurement_order(models.Model):
    _inherit = 'procurement.order'

    lot_id = fields.Many2one('stock.production.lot', 'Lot')

    @api.model
    def _get_stock_move_values(self):
        res = super(
            procurement_order, self)._get_stock_move_values()
        res['restrict_lot_id'] = self.lot_id.id
        return res

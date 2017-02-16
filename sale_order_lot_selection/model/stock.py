
# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com).
# @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _prepare_procurement_from_move(self, move):
        vals = super(StockMove, self)._prepare_procurement_from_move(move)
        vals['lot_id'] = move.restrict_lot_id.id
        return vals


# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com).
# @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _prepare_procurement_values(self):
        res = super(
            StockMove, self)._prepare_procurement_values()
        res['lot_id'] = self.lot_id.id if self.lot_id else False
        return res

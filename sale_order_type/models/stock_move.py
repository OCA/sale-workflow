# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _prepare_picking_assign(self, move):
        values = super(StockMove, self)._prepare_picking_assign(move)
        if move.procurement_id.sale_line_id:
            move.procurement_id.sale_line_id.order_id
        return values

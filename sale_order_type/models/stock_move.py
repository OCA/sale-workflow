# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _prepare_picking_assign(self, move):
        values = super(StockMove, self)._prepare_picking_assign(move)
        if move.procurement_id.sale_line_id:
            sale = move.procurement_id.sale_line_id.order_id
            values['invoice_state'] = sale.type_id.invoice_state
        return values

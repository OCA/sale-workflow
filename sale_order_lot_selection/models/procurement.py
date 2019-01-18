from odoo import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    lot_id = fields.Many2one('stock.production.lot', 'Lot')

    @api.model
    def _get_stock_move_values(self):
        res = super(
            ProcurementOrder, self)._get_stock_move_values()
        res['restrict_lot_id'] = self.lot_id.id
        return res

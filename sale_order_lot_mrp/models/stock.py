# coding: utf-8
# © 2014 ToDay Akretion
# @author  Florian DA COSTA <florian.dacosta@akretion.com>
# @author  Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_lot_vals(self, old_lot, index):
        self.ensure_one()
        lot_number = "%s-%d" % (
            old_lot.name, index)
        return {
            'name': lot_number,
            'product_id': self.product_id.id
        }

    def action_explode(self):
        original_lot = self.restrict_lot_id
        processed_moves = super(StockMove, self.with_context(subcall=True)).\
            action_explode()
        if not self.env.context.get('subcall', False) and processed_moves and \
                original_lot:
            index = 1
            for new_move in processed_moves:
                if new_move != self:
                    vals = new_move._get_lot_vals(original_lot, index)
                    lot = original_lot.copy(vals)
                    new_move.restrict_lot_id = lot
                    index += 1

        return processed_moves


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    mrp_production_ids = fields.One2many(
        'mrp.production',
        'lot_id',
        string='Production Order')

    @api.multi
    def unlink(self):
        for lot in self:
            for mo in lot.mrp_production_ids:
                mo.unlink()
        return super(StockProductionLot, self).unlink()

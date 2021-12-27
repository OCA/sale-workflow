# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    picking_note = fields.Text(
        string="Picking Note",
    )
    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if vals.get('picking_note', False):
            for rec in self:
                stock_moves = self.env['stock.move'].search([('procurement_id.sale_line_id.order_id', '=', rec.id), ('state', 'not in', ('done', 'cancel'))])
                for picking in stock_moves.mapped('picking_id'):
                    picking.note = vals.get('picking_note', False)
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        sale_note = self.procurement_id.sale_line_id.order_id.picking_note
        if sale_note:
            vals['note'] = sale_note
        return vals

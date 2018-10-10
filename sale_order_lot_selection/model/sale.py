# -*- coding: utf-8 -*-
# © 2015 Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.exceptions import Warning


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot', copy=False)

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        res = super(
            SaleOrderLine, self)._prepare_procurement_values(
            group_id=group_id)
        res['lot_id'] = self.lot_id.id if self.lot_id else False
        return res

    @api.model
    def get_stock_move_line_for_lot(self):
        self.ensure_one()
        lot_count = 0
        move = self.env['stock.move.line']
        for stock_move in self.move_ids:
            for m in stock_move.move_line_ids:
                if self.lot_id == m.lot_id:
                    lot_count += 1
                    move = m
                    # if counter is 0 or > 1 means that something goes wrong
                    if lot_count != 1:
                        raise Warning(_('Can\'t retrieve lot on stock'))
        return move

    @api.model
    def _check_move_state(self):
        self.ensure_one()
        if self.lot_id:
            move = self.get_stock_move_line_for_lot()
            if move.state == 'confirmed':
                move.action_assign()
                move.refresh()
            if move.state != 'assigned':
                raise Warning(_('Can\'t reserve products for lot %s') %
                              self.lot_id.name)
        return True


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for line in self.order_line:
            line._check_move_state()
        return res

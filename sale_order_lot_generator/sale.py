# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for Odoo
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_vals_lot_number(self, order_line, index_lot):
        """Prepare values before creating a lot number"""
        lot_number = "%s-%02d" % (order_line.order_id.name, index_lot)
        return {
            'name': lot_number,
            'product_id': order_line.product_id.id,
            # in V8 company_id doesn't exist
            # 'company_id': order_line.order_id.company_id.id,
        }

    @api.one
    def generate_prodlot(self):
        lot_m = self.env['stock.production.lot']
        index_lot = 1
        for line in self.order_line:
            line_vals = {}
            if line.product_id.auto_generate_prodlot and not line.lot_id:
                vals = self._prepare_vals_lot_number(line, index_lot)
                index_lot += 1
                lot_id = lot_m.create(vals)
                line_vals['lot_id'] = lot_id.id
                line.write(line_vals)

    @api.multi
    def action_ship_create(self):
        self.ensure_one()
        self.generate_prodlot()
        return super(SaleOrder, self).action_ship_create()

    @api.model
    def _prepare_order_line_move(self, order, line, picking_id, date_planned):
        """ original method is in module purchase/purchase.py """
        result = super(SaleOrder, self)._prepare_order_line_move(
            order, line, picking_id, date_planned)
        result.update({'restrict_lot_id': line.lot_id.id})
        return result

    @api.model
    def _check_move_state(self, line):
        if not line.product_id.auto_generate_prodlot:
            return super(SaleOrder, self)._check_move_state(line)
        else:
            return True

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for sale in self:
            for line in sale.order_line:
                line.lot_id.unlink()
        return res

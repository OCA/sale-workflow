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

from openerp import fields, api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    lot_id = fields.Many2one(
                             'stock.production.lot',
                             string='Serial Number',
                             readonly=True
                            )


    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['lot_id'] = False
        return super(SaleOrderLine, self).copy_data(
            cr, uid, id, default, context=context)

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.model
    def _prepare_vals_lot_number(self, order_line_id, index_lot):
        """Prepare values before creating a lot number"""
        order_line = self.env['sale.order.line'].browse(order_line_id)
        lot_number = "%s-%02d" % (order_line.order_id.name, index_lot)
        return {
            'name': lot_number,
            'product_id': order_line.product_id.id,
            # in V8 company_id doesn't exist
            #'company_id': order_line.order_id.company_id.id,
        }

    @api.multi
    def action_ship_create(self):
        self.ensure_one()
        lot_m = self.env['stock.production.lot']
        for sale_order in self:
            index_lot = 1
            for line in sale_order.order_line:
                line_vals = {}
                if line.product_id.track_from_sale:
                    vals = self._prepare_vals_lot_number(
                        line.id, index_lot)
                    index_lot += 1
                    lot_id = lot_m.create(vals)
                    line_vals['lot_id'] = lot_id.id
                line_vals.update(self._prepare_sale_line(line))
                if line_vals:
                    line.write(line_vals)
        return super(SaleOrder, self).action_ship_create()

    @api.model
    def _prepare_order_line_move(self, order, line, picking_id, date_planned):
        """ original method is in module purchase/purchase.py """
        result = super(SaleOrder, self)._prepare_order_line_move(
            order, line, picking_id, date_planned)
        result.update({'lot_id': line.lot_id.id})
        return result

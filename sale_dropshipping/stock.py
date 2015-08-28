# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm


class StockMove(orm.Model):
    _inherit = "stock.move"

    def _update_average_price(self, cr, uid, move, context=None):
        # In case of a purchase done by a dropshipping,
        # no "in" stock move is created, but the price
        # should be recomputed if needed
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')

        product = move.product_id
        if (product.is_direct_delivery_from_product and
                product.cost_method == 'average'):
            # Use the new price (no need to average)
            new_price = currency_obj.compute(
                cr, uid, move.price_currency_id.id,
                move.company_id.currency_id.id,
                move.price_unit, round=False)
            new_price = uom_obj._compute_price(
                cr, uid, move.product_uom.id,
                new_price, product.uom_id.id)

            product_obj.write(
                cr, uid, [product.id], {'standard_price': new_price},
                context=context)
        else:
            return super(StockMove)._update_average_price(
                cr, uid, move, context=context)

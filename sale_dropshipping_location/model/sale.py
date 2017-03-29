# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              Jordi Ballester Alomar <jordi.ballester@eficent.com>
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

from openerp.osv import fields, orm


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id,
                                        date_planned, context=None):
        res = super(
            sale_order, self)._prepare_order_line_procurement(
                cr, uid, order, line,
                move_id, date_planned,
                context)

        if line.sale_flow in [
            'direct_delivery', 'direct_invoice_and_delivery'
        ]:
            res['location_id'] = order.shop_id.warehouse_id.lot_stock_id.id
        return res
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


class purchase_order(orm.Model):
    _inherit = "purchase.order"

    def sale_flow_change(self, cr, uid, ids, sale_flow, sale_id,
                         warehouse_id, context=None):
        res = super(purchase_order, self).sale_flow_change(
            cr, uid, ids, sale_flow, sale_id, warehouse_id, context=context)

        if sale_flow in ('direct_delivery', 'direct_invoice_and_delivery'):
            if 'value' in res and 'location_id' in res['value']:
                warehouse_obj = self.pool.get('stock.warehouse')
                warehouse = warehouse_obj.browse(
                    cr, uid, warehouse_id, context=context)
                if warehouse.property_stock_drop_ship:
                    res['value']['location_id'] = \
                        warehouse.property_stock_drop_ship.id
        return res
# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2013 Camptocamp SA
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
import datetime
from openerp.osv import orm
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT)


class sale_order_line(orm.Model):
    """Adds two exception functions to be called by the sale_exceptions module.

    The first one will ensure that an order line can be delivered on the
    delivery date, if the related product is in MTS. Validation is done by
    using the shop related to the sales order line location and using the line
    delay.
    The second one will raise a sales exception if the current SO will break an
    order already placed in future

    """

    _inherit = "sale.order.line"

    def _compute_line_delivery_date(self, line_br, context=None):
        date_order = line_br.order_id.date_order
        date_order = datetime.datetime.strptime(date_order,
                                                DEFAULT_SERVER_DATE_FORMAT)
        # delay is a float, that is perfectly supported by timedelta
        return date_order + datetime.timedelta(days=line_br.delay)

    def _get_line_location(self, line_br, context=None):
        return line_br.order_id.shop_id.warehouse_id.lot_stock_id.id

    def can_command_at_delivery_date(self, cr, uid, l_id, context=None):
        """Predicate that checks whether a SO line can be delivered at delivery date.

        Delivery date is computed using date of the order + line delay.
        Location is taken from the shop linked to the line

        :return: True if line can be delivered on time

        """
        if context is None:
            context = {}
        prod_obj = self.pool['product.product']
        if isinstance(l_id, (tuple, list)):
            assert len(l_id) == 1, "Only one id supported"
            l_id = l_id[0]
        line = self.browse(cr, uid, l_id, context=context)
        if not line.product_id or line.type != 'make_to_stock':
            return True
        delivery_date = self._compute_line_delivery_date(line, context=context)
        ctx = context.copy()
        ctx['to_date'] = delivery_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        ctx['location'] = self._get_line_location(line, context=context)
        ctx['compute_child'] = True  # Virtual qty is made on all childs of chosen location
        prod_for_virtual_qty = prod_obj.read(cr, uid, line.product_id.id,
                                             ['virtual_available'], context=ctx)
        if prod_for_virtual_qty['virtual_available'] < line.product_uom_qty:
            return False
        return True

    def _get_states(self):
        return ('waiting', 'confirmed', 'assigned')

    def _get_affected_dates(self, cr, location_id, product_id, delivery_date, context=None):
        """Determine future dates where virtual stock has to be checked.

        It will only look for stock move that pass by location_id.
        If your stock location have children or you have configured automated stock action
        they must pass by the location related to SO line, else the will be ignored

        :param location_id: location id to be checked
        :param product_id: product id te be checked

        :return: list of dates to be checked

        """
        sql = ("SELECT date FROM stock_move"
               "  WHERE state IN %s"
               "   AND date > %s"
               "   AND product_id = %s"
               "   AND location_id = %s")
        cr.execute(sql, (self._get_states(),
                         delivery_date,
                         product_id,
                         location_id))
        return (row[0] for row in cr.fetchall())

    def future_orders_are_affected(self, cr, uid, l_id, context=None):
        """Predicate function that is a naive workaround for the lack of stock reservation.

        This can be a performance killer, you should not use it
        if you have constantly a lot of running Orders

        :return: True if future order are affected by current command line
        """
        if context is None:
            context = {}
        prod_obj = self.pool['product.product']
        if isinstance(l_id, (tuple, list)):
            assert len(l_id) == 1, "Only one id supported"
            l_id = l_id[0]
        line = self.browse(cr, uid, l_id, context=context)
        if not line.product_id or not line.type == 'make_to_stock':
            return False
        delivery_date = self._compute_line_delivery_date(line, context=context)
        ctx = context.copy()
        location_id = self._get_line_location(line, context=context)
        ctx['location'] = location_id
        ctx['compute_child'] = True  # Virtual qty is made on all childs of chosen location
        dates = self._get_affected_dates(cr, location_id, line.product_id.id,
                                         delivery_date, context=context)
        for aff_date in dates:
            ctx['to_date'] = aff_date
            prod_for_virtual_qty = prod_obj.read(cr, uid, line.product_id.id,
                                                 ['virtual_available'], context=ctx)
            if prod_for_virtual_qty['virtual_available'] < line.product_uom_qty:
                return True
        return False

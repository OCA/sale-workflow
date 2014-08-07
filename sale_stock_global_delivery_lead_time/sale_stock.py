# -*- coding: utf-8 -*-
#
#
#    Author: Alexandre Fayolle
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
#
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _min_max_date_planned(
        self, cr, uid, ids, field_names, arg, context=None
    ):
        res = {}
        if not ids:
            return res
        order_line_obj = self.pool.get('sale.order.line')
        sale_infos = self.read(cr, uid, ids,
                               ['delay', 'date_order'],
                               context=context,
                               load='_classic_write')
        line_ids = order_line_obj.search(cr, uid,
                                         [('order_id', 'in', ids)],
                                         context=context)
        line_delays = order_line_obj.read(cr, uid, line_ids,
                                          ['order_id', 'delay'],
                                          context=context,
                                          load='_classic_write')
        order_line_delays = {}  # dict order_id: [line delays]
        for line_info in line_delays:
            order_line_delays.setdefault(
                line_info['order_id'], []).append(line_info['delay'])
        for sale_info in sale_infos:
            sale_id = sale_info['id']
            res[sale_id] = {}
            start_date = datetime.strptime(
                self.date_to_datetime(
                    cr, uid, sale_info['date_order'], context),
                DEFAULT_SERVER_DATETIME_FORMAT)
            min_delay = sale_info['delay'] + min(
                order_line_delays.get(sale_id, [0]))
            max_delay = sale_info['delay'] + max(
                order_line_delays.get(sale_id, [0]))
            min_date = start_date + relativedelta(days=min_delay)
            max_date = start_date + relativedelta(days=max_delay)
            for name in field_names:
                if name == 'min_date_planned':
                    date = min_date
                elif name == 'max_date_planned':
                    date = max_date
                else:
                    continue
                res[sale_id][name] = date.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
        return res

    _columns = {
        'delay': fields.float('Delivery Lead Time',
                              required=True,
                              help="Number of days between the order "
                                   "confirmation and the shipping of the "
                                   "products "
                                   "to the customer. This lead time is added "
                                   "to the lead time of each line.",
                              readonly=True,
                              states={'draft': [('readonly', False)]}),
        'min_date_planned': fields.function(_min_max_date_planned,
                                            type='date',
                                            string='Earliest date planned',
                                            method=True, multi='date_planned'),
        'max_date_planned': fields.function(_min_max_date_planned,
                                            type='date',
                                            string='Latest date planned',
                                            method=True, multi='date_planned'),
    }
    _defaults = {'delay': 0,
                 }

    def _get_date_planned(
        self, cr, uid, order, line, start_date, context=None
    ):
        date_planned = super(
            sale_order, self)._get_date_planned(cr, uid, order,
                                                line, start_date,
                                                context)
        date_planned = datetime.strptime(date_planned,
                                         DEFAULT_SERVER_DATETIME_FORMAT)
        date_planned += relativedelta(days=order.delay or 0.0)
        return date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

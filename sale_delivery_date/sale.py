# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'expected_date': fields.date('Expected Delivery Date', required=True),
    }

    def _get_date_planned(self, cr, uid,
                          order, line, start_date, context=None):
        # Totally overridden; the planned date is the one entered on the SO.
        # However, we calculate the real delay when it happens.
        start_date = self.date_to_datetime(cr, uid, start_date, context)
        expected_date = self.date_to_datetime(cr, uid,
                                              order.expected_date, context)
        date_difference = datetime.strptime(expected_date,
                                            DEFAULT_SERVER_DATETIME_FORMAT) - \
            datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT)
        delay = date_difference.days + order.company_id.security_lead
        line.write({'delay': delay})
        return order.expected_date

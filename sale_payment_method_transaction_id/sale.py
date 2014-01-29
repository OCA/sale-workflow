# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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

from openerp.osv import orm


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _prepare_payment_move_line(self, cr, uid, move_name, sale, journal,
                                   period, amount, date, context=None):
        debit_line, credit_line = super(sale_order, self).\
            _prepare_payment_move_line(cr, uid, move_name, sale, journal,
                                       period, amount, date, context=context)
        if sale.transaction_id:
            debit_line['transaction_ref'] = sale.transaction_id
            credit_line['transaction_ref'] = sale.transaction_id
        return debit_line, credit_line

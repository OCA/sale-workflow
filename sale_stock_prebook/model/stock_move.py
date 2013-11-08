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
from osv import fields, osv
"""Add expiry date on pre-booked stock move"""


class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
        'date_validity': fields.date('Validity Date'),
    }

    def init(self, cr):
        """ Index date_validity if filled """
        indexname = 'stock_move_date_validity_index'
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', (indexname,))
        if not cr.fetchone():
            cr.execute("""CREATE INDEX %s ON %s (date_validity)
                          WHERE date_validity IS NOT NULL""" % (indexname, self._table))

    def _is_prebooked(self, move):
        return move.date_validity and move.state == 'waiting' and move.picking_id.id is False

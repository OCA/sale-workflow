# -*- coding: utf-8 -*-

from osv import fields, osv
from tools.translate import _
from openerp import SUPERUSER_ID

"""
* Add expiry date on pre-booked stock move
"""

#TODO: cron job to cancell pre-bookings based on validity date

class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
        'date_validity': fields.date('Validity Date'),
    }
    def init(self, cr):
        """ Index date_validity if filled """
        indexname='stock_move_date_validity_index'
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', (indexname,))
        if not cr.fetchone():
            cr.execute('CREATE INDEX %s ON %s (date_validity) WHERE date_validity IS NOT NULL'%(indexname,self._table))
    def _is_prebooked(self,move):
        return move.date_validity and move.state == 'waiting' and move.picking_id.id is False


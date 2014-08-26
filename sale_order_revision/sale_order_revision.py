# -*- encoding: utf-8 -*-
#
# OpenERP, Open Source Management Solution
# This module copyright (C) 2013 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

import logging

_logger = logging.getLogger(__name__)
logging.basicConfig()
_logger.setLevel(logging.DEBUG)

from openerp.osv import fields, orm


class sale_order_revision(orm.Model):
    """ Add the notion of revision to sale.order """
    _inherit = 'sale.order'

    _columns = {
        'revision': fields.many2one('sale.order', 'Revision', readonly=True),
        # This could have been a test like bool(record.revision), but I prefered to
        # store the value in the database, it will be faster and not so footprint heavy
        'revised': fields.boolean('status', readonly=True),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """ Override of the copy method to add a link between the
        copied record and the copy.

        :return: record id
        """
        records = self.pool.get(self._inherit)
        current_record = records.browse(cr, uid, id)

        # Regular copy
        new_record_id = super(sale_order_revision, self).copy(cr, uid, id, default=default, context=context)
        new_record = records.browse(cr, uid, new_record_id)

        # creating a new record with the revision to the current record.
        new_record.write({'revision': current_record.id})

        # Adding the revision of the record to the new record.
        # Also updating revised to indicate the record is revised.
        current_record.write({'revised': True, 'revision': new_record_id})

        # The standard copy() method returns the id of the copy.
        return new_record_id

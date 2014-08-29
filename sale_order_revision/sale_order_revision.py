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
from openerp.tools.translate import _


class sale_order_revision(orm.Model):
    """ Add the notion of revision to sale.order """
    _inherit = 'sale.order'

    _columns = {
        'revision_of': fields.many2one(_inherit, 'Revision of', readonly=True),
        'revised_by': fields.many2one(_inherit, 'Revised by', readonly=True),
        # This could have been a test like bool(record.revision), but I prefered to
        # store the value in the database, it will be faster and not so footprint heavy
        'revised': fields.boolean('status', readonly=True),
        'revision_original_id': fields.many2one(_inherit, 'Original Sale Order', readonly=True),
        'number_revisions': fields.integer('Number of Revisions', readonly=True)
    }

    def create_revision(self, cr, uid, id_, default=None, context=None):
        """ Create a copy of the current record and add data to link the two records.

        :return: View descriptor
        """
        # We need the id as int here.
        if isinstance(id_, list):
            id_ = id_[0]

        records = self.pool.get(self._inherit)
        current_record = records.browse(cr, uid, id_)

        # Regular copy
        new_record_id = self.copy(cr, uid, id_, default=default, context=context)
        new_record = records.browse(cr, uid, new_record_id)
        new_record.write({
            'revision_of': current_record.id,
            'revised_by': None,
            'revised': False,
            })

        revisions = track_revisions(
            cr, uid,
            new_record,
            records,
            []
        )
        #Cancel the record and all its lines
        self.action_cancel(cr, uid, id_, context)

        _logger.debug('Revisions: {}'.format(revisions))
        # creating a new record with the revision to the current record.
        new_record.write({
            'revision_original_id': revisions[0].id,
            'number_revisions': len(revisions),
        })

        # Adding the revision of the record to the new record.
        # Also updating revised to indicate the record is revised.
        current_record.write({
            'revised': True,
            'revised_by': new_record_id
        })


        # redisplay the record as a sales order
        # code extracted from sale/sale.py (action_button_confirm method)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,

        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order Revision'),
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'nodestroy': True,
            'res_id': new_record_id,
            'target': 'current',
            }

def track_revisions(cr, uid, record, registry, revisions):
    """ recursively track previous revisions of a given record.
    :param record: record to find from.
    :param registry: registry to look in.
    :param revisions: list of revisions.
    :return: list of revisions
    """
    previous_record = record.revision_of
    _logger.debug('previous_record: {}'.format(previous_record))
    _logger.debug('previous_record.id: {}'.format(previous_record.id))

    # Testing if the record has a revision of itself
    # to know if we need to keep on tracking.
    if previous_record.revision_of:
        track_revisions(cr, uid, previous_record, registry, revisions)

    revisions.append(previous_record)

    return revisions

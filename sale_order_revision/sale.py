# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    @author Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#    @author Raphaël Valyi <raphael.valyi@akretion.com> (ported to sale from
#    original purchase_order_revision by Lorenzo Battistini)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import netsvc
from openerp.osv import fields, orm
from openerp.tools.translate import _


class sale_order(orm.Model):

    _inherit = "sale.order"

    _columns = {
        'current_revision_id': fields.many2one(
            'sale.order', 'Current revision', readonly=True),
        'old_revision_ids': fields.one2many(
            'sale.order', 'current_revision_id',
            'Old revisions', readonly=True),
        }

    def copy_quotation(self, cr, uid, ids, context=None):
        if len(ids) > 1:
            raise orm.except_orm(
                _('Error'), _('This only works for 1 SO at a time'))
        so = self.browse(cr, uid, ids[0], context)
        new_seq = self.pool.get('ir.sequence').get(
            cr, uid, 'sale.order') or '/'
        old_seq = so.name
        so.write({'name': new_seq}, context=context)
        # 'orm.Model.copy' is called instead of 'self.copy' in order to avoid
        # 'sale.order' method to overwrite our values, like name and state
        orm.Model.copy(self, cr, uid, so.id, default={
            'name': old_seq,
            'state': 'cancel',
            'shipped': False,
            'invoiced': False,
            'invoice_ids': [],
            'picking_ids': [],
            'old_revision_ids': [],
            'current_revision_id': so.id,
            }, context=None)
        self.write(cr, uid, ids, {'state':'draft','shipped':0})
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_delete(uid, 'sale.order', ids[0], cr)
        wf_service.trg_create(uid, 'sale.order', ids[0], cr)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'old_revision_ids': [],
        })
        return super(sale_order, self).copy(cr, uid, id, default, context)

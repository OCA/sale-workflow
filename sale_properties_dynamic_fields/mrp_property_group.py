# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl
#    (<http://www.agilebg.com>)
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import exceptions


class MrpPropertyGroup(orm.Model):
    _inherit = 'mrp.property.group'
    _columns = {
        # TODO: rename method when porting to Odoo v9
        'draw_dynamically': fields.boolean(
            'Display dynamically',
            help='In sale order line, display this property dynamically, '
                 'as text field'),
        'field_id': fields.many2one('ir.model.fields', 'Field', readonly=True),
    }

    def build_field_vals(self, cr, uid, group, context=None):
        model_pool = self.pool['ir.model']
        model_ids = model_pool.search(
            cr, uid, [('model', '=', 'sale.order.line')], context=context)
        field_name = 'x_' + group.name.lower()
        return {
            'name': field_name,
            'model': 'sale.order.line',
            'model_id': model_ids[0],
            'field_description': group.name,
            'ttype': 'char',
            'state': 'manual'
        }

    def check_duplicate_field(self, cr, uid, field_id, context=None):
        field_pool = self.pool['ir.model.fields']
        field = field_pool.browse(cr, uid, field_id, context=context)
        field_ids = field_pool.search(cr, uid, [
            ('name', '=', field.name),
            ('model', '=', 'sale.order.line'),
        ],
            context=context)
        if len(field_ids) > 1:
            raise exceptions.Warning(
                _('Field %s (sale.order.line) already present')
                % field.name)
        return True

    def create(self, cr, uid, vals, context=None):
        res = super(MrpPropertyGroup, self).create(
            cr, uid, vals, context=context)
        group = self.browse(cr, uid, res, context=context)
        if group.draw_dynamically:
            field_pool = self.pool['ir.model.fields']
            field_id = field_pool.create(cr, uid, self.build_field_vals(
                cr, uid, group, context=context))
            self.check_duplicate_field(cr, uid, field_id, context=context)
            self.write(cr, uid, [res], {
                'field_id': field_id,
            }, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        res = super(MrpPropertyGroup, self).write(
            cr, uid, ids, vals, context=context)
        if 'draw_dynamically' not in vals:
            # update field_id only when changing draw_dynamically field
            return res
        field_pool = self.pool['ir.model.fields']
        for group in self.browse(cr, uid, ids, context=context):
            if group.draw_dynamically and not group.field_id:
                field_id = field_pool.create(
                    cr, uid, self.build_field_vals(
                        cr, uid, group, context=context))
                self.check_duplicate_field(cr, uid, field_id, context=context)
                self.write(cr, uid, [group.id], {
                    'field_id': field_id,
                }, context=context)
            if not group.draw_dynamically and group.field_id:
                context['_force_unlink'] = True
                field_pool.unlink(
                    cr, uid, [group.field_id.id], context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        for group in self.browse(cr, uid, ids, context=context):
            if group.field_id:
                ctx['_force_unlink'] = True
                group.field_id.unlink(context=ctx)
        res = super(MrpPropertyGroup, self).unlink(
            cr, uid, ids, context=ctx)
        return res

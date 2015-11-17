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


class MrpProperty(orm.Model):
    _inherit = 'mrp.property'
    _columns = {
        'value': fields.char('Value', size=64),
    }

    def name_create(self, cr, uid, name, context=None):
        """
        This allows the user to digit 'width 0.5' and the system will
        automatically create a property of group 'width' with value '0.5'
        """
        splitted_name = name.split()
        if len(splitted_name) == 2:
            group_ids = self.pool['mrp.property.group'].search(
                cr, uid, [('name', '=', splitted_name[0])], context=context)
            if group_ids and len(group_ids) == 1:
                rec_id = self.create(cr, uid, {
                    'name': name,
                    'group_id': group_ids[0],
                    'value': splitted_name[1]
                }, context=context)
                return self.name_get(cr, uid, [rec_id], context)[0]
        return super(MrpProperty, self).name_create(
            cr, uid, name, context=context)

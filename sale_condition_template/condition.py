# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi
#    Copyright 2013-2014 Camptocamp SA
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
from osv import osv, fields


class AccountConditionText(osv.osv):

    """add info condition in the invoice"""
    _name = "account.condition_text"
    _description = "Invoice condition text"

    _columns = {'name': fields.char('Condition', required=True, size=128),
                'type': fields.selection([('header', 'Header'),
                                          ('footer', 'Footer')],
                                         'type',
                                         required=True),
                'text': fields.text('text', translate=True, required=True)}

    def get_value(self, cursor, uid, cond_id, field_name, partner_id=False):
        if not cond_id:
            return {}
        part_obj = self.pool.get('res.partner')
        text = ''
        try:
            lang = part_obj.browse(cursor, uid, partner_id).lang
        except:
            lang = 'en_US'
        cond = self.browse(cursor, uid, cond_id, {'lang': lang})
        text = cond.text
        return {'value': {field_name: text}}


AccountConditionText()

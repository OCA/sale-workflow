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
from openerp.osv import orm, fields


class AccountInvoice(orm.Model):

    """Add text condition"""

    _inherit = "account.invoice"
    _columns = {
        'condition_template1_id': fields.many2one('base.condition_template',
                                                  'Top conditions'),
        'condition_template2_id': fields.many2one('base.condition_template',
                                                  'Bottom conditions'),
        'note1': fields.html('Top conditions'),
        'note2': fields.html('Bottom conditions'),
    }

    def set_condition(self, cr, uid, cond_id, field_name, partner_id):
        if not cond_id:
            return {'value': {field_name: ''}}
        cond_obj = self.pool['base.condition_template']
        text = cond_obj.get_value(cr, uid, cond_id, partner_id)
        return {'value': {field_name: text}}

    def set_note1(self, cr, uid, inv_id, cond_id, partner_id):
        return self.set_condition(cr, uid, cond_id, 'note1', partner_id)

    def set_note2(self, cr, uid, inv_id, cond_id, partner_id):
        return self.set_condition(cr, uid, cond_id, 'note2', partner_id)

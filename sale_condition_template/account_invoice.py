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


class AccountInvoice(osv.osv):

    """Add text condition"""

    _inherit = "account.invoice"
    _columns = {
        'text_condition1': fields.many2one('account.condition_text', 'Header'),
        'text_condition2': fields.many2one('account.condition_text', 'Footer'),
        'note1': fields.text('Header'),
        'note2': fields.text('Footer')}

    def set_condition(
        self, cursor, uid, inv_id, cond_id, field_name, partner_id
    ):
        cond_obj = self.pool.get('account.condition_text')
        return cond_obj.get_value(cursor, uid, cond_id, field_name, partner_id)

AccountInvoice()

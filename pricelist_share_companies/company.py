# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2011 Camptocamp SA
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


class ResCompany(orm.Model):

    '''Override company to add the fields to use for the prices'''
    _inherit = 'res.company'

    def _price_field_get(self, cr, uid, context=None):
        if context is None:
            context = {}
        mf = self.pool.get('ir.model.fields')
        ids = mf.search(cr, uid,
                        [
                            ('model', 'in', (
                                ('product.product'), ('product.template')
                            )),
                            ('ttype', '=', 'float')],
                        context=context)
        res = [(False, '')]
        for field in mf.browse(cr, uid, ids, context=context):
            res.append((field.name, field.field_description))
        return res

    _columns = {
        'standard_price_field': fields.selection(
            _price_field_get, 'Field for Cost Price', size=32,
            required=True,
            help="If a field is selected, it will be used instead of the "
                 "\"standard_price\" field"
                 "on the search of a Cost Price's Price Type.")
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camtocamp SA
# @author Guewen Baconnier
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields, osv


class ResCompany(osv.osv):
    """Override company to add the fields to use for the prices"""
    _inherit = 'res.company'

    def _price_field_get(self, cr, uid, context=None):
        mf = self.pool.get('ir.model.fields')
        ids = mf.search(cr, uid,
                        [('model','in', (('product.product'),('product.template'))),
                         ('ttype','=','float')],
                        context=context)
        res = [(False, '')]
        for field in mf.browse(cr, uid, ids, context=context):
            res.append((field.name, field.field_description))
        return res

    _columns = {
        'standard_price_field': fields.selection(_price_field_get, 'Field for Cost Price', size=32,
            required=True,
            help="If a field is selected, it will be used instead of the \"standard_price\" field"
                 "on the search of a Cost Price's Price Type.")
    }

ResCompany()

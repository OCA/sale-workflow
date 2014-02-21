# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Romain Deheele
#    Copyright 2014 Camptocamp SA
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
##############################################################################

from openerp.osv import orm, fields


class product_template(orm.Model):

    _inherit = 'product.template'

    def get_procurement_type_selection(self, cr, uid, context=None):
        """
        Has to be inherited to add procurement type
        """
        return [('standard', 'Standard'),
                ('bom', 'Bill of Materials')]

    def _compute_procurement_vals(self, vals):
        if vals['procurement_type'] == 'standard':
            vals.update({'procure_method': 'make_to_stock',
                         'supply_method': 'buy',
                         })
        elif vals['procurement_type'] == 'bom':
            vals.update({'procure_method': 'make_to_order',
                         'supply_method': 'produce',
                         })
        return vals

    _columns = {
        'procurement_type': fields.selection(
            get_procurement_type_selection,
            'Procurement Type',
            required=True,
            help='Standard: Procurement Method: Make to Stock, '
                 'Supply Method: Buy.\n'
                 'Bill of Materials: Procurement Method: Make to Order, '
                 'Supply Method: Produce.\n'),
    }

    _defaults = {
        'procurement_type': 'standard',
    }

    def onchange_procurement_type(self, cr, uid, ids, type, procurement_type,
                                  context=None):
        vals = {'procurement_type': procurement_type}
        if type != 'service':
            vals = self._compute_procurement_vals(vals)
        return {'value': vals}

    def write(self, cr, uid, ids, vals, context=None):
        for product in self.read(cr, uid, ids, ['type'], context=context):
            if product['type'] != 'service' and \
                    vals.get('procurement_type'):
                vals = self._compute_procurement_vals(vals)
        res = super(product_template, self).write(cr, uid, ids, vals,
                                                  context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        if vals['type'] != 'service' and vals.get('procurement_type'):
            vals = self._compute_procurement_vals(vals)
        return super(product_template, self).create(cr, uid, vals,
                                                    context=context)


class product_product(orm.Model):

    _inherit = 'product.product'

    def onchange_procurement_type(self, cr, uid, ids, type, procurement_type,
                                  context=None):
        tmpl_obj = self.pool['product.template']
        res = tmpl_obj.onchange_procurement_type(cr, uid, ids, type,
                                                 procurement_type,
                                                 context=context)
        return {'value': res['value']}

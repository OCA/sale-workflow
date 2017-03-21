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
import logging

from openerp.osv import orm, fields

_logger = logging.getLogger('openerp.upgrade')

def get_procurement_type_selection():
    return [('buy_stock', 'On stock, buy'),
            ('buy_demand', 'On demand, buy'),
            ('produce_demand', 'On demand, produce'),
            ('produce_stock', 'On stock, produce'),
            ]

class product_template(orm.Model):

    _inherit = 'product.template'

    def init(self, cr):
        _logger.info('Migrating product_procurement_type')
        query = ("UPDATE product_template pt "
                 "SET procurement_type=%(procurement_type)s "
                 "WHERE procure_method=%(procure_method)s and supply_method=%(supply_method)s")
        fixes = [{'procurement_type': 'buy_stock',
                  'procure_method': 'make_to_stock',
                  'supply_method': 'buy'},
                 {'procurement_type': 'buy_demand',
                  'procure_method': 'make_to_order',
                  'supply_method': 'buy'},
                 {'procurement_type': 'produce_stock',
                  'procure_method': 'make_to_stock',
                  'supply_method': 'produce'},
                 {'procurement_type': 'produce_demand',
                  'procure_method': 'make_to_order',
                  'supply_method': 'produce'},
                 ]
        for fix in fixes:
            cr.execute(query, fix)

    def get_procurement_type_selection(self, cr, uid, context=None):
        """
        Has to be inherited to add procurement type
        """
        return get_procurement_type_selection()

    def _compute_procurement_vals(self, vals):
        if vals['procurement_type'] == 'buy_stock':
            vals.update({'procure_method': 'make_to_stock',
                         'supply_method': 'buy',
                         })
        elif vals['procurement_type'] == 'produce_demand':
            vals.update({'procure_method': 'make_to_order',
                         'supply_method': 'produce',
                         })
        elif vals['procurement_type'] == 'buy_demand':
            vals.update({'procure_method': 'make_to_order',
                         'supply_method': 'buy',
                         })
        elif vals['procurement_type'] == 'produce_stock':
            vals.update({'procure_method': 'make_to_stock',
                         'supply_method': 'produce',
                         })
        else:
            vals['procurement_type'] = False
        return vals

    _columns = {
        'procurement_type': fields.selection(
            get_procurement_type_selection,
            'Procurement Type',
            required=True,
            help='On stock, buy: Procurement Method: Make to Stock, '
                 'Supply Method: Buy.\n'
                 'On stock, produce: Procurement Method: Make to Stock, '
                 'Supply Method: Produce.\n'
                 'On order, buy: Procurement Method: Make to Order, '
                 'Supply Method: Buy.\n'
                 'On order, produce: Procurement Method: Make to Order, '
                 'Supply Method: Produce.\n'
            ),
    }

    _defaults = {
        'procurement_type': 'buy_stock',
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

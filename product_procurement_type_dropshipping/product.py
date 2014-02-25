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
from openerp.tools.translate import _


class product_template(orm.Model):

    _inherit = 'product.template'

    def get_procurement_type_selection(self, cr, uid, context=None):
        """
        Adds type dropshipping in procurement_type selection
        """
        res = super(product_template, self).get_procurement_type_selection(
            cr, uid, context=context)
        res.append(('direct_delivery', 'Drop Shipping'))
        return res

    def _compute_procurement_vals(self, vals):
        if vals['procurement_type'] == 'direct_delivery':
            vals.update({'procure_method': 'make_to_order',
                         'supply_method': 'buy',
                         })
        else:
            vals = super(product_template, self)._compute_procurement_vals(vals)
        return vals

    def _check_sellers(self, cr, uid, ids, procurement_type, context=None):
        dd_flag = procurement_type == 'direct_delivery'
        seller_pool = self.pool['product.supplierinfo']
        seller_ids = seller_pool.search(cr, uid, [('product_id', 'in', ids)],
                                        context=context)
        if seller_ids:
            seller_pool.write(cr, uid, seller_ids,
                              {'direct_delivery_flag': dd_flag},
                              context=context)
        else:
            if dd_flag:
                raise orm.except_orm(
                    _('Warning!'),
                    _('No suppliers defined'))

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
                 'DropShipping: Procurement Method: Make to Order, '
                 'Supply Method: Buy.'),
    }

    def onchange_procurement_type(self, cr, uid, ids, type,
                                  procurement_type, context=None):
        res = super(product_template, self).\
            onchange_procurement_type(cr,
                                      uid,
                                      ids,
                                      type,
                                      procurement_type)
        if type != 'service':
            res['value'].update(
                self._compute_procurement_vals(
                    {'procurement_type': procurement_type})
                )
            self._check_sellers(cr, uid, ids, procurement_type,
                                context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        for product in self.read(cr, uid, ids, ['type'], context=context):
            if product['type'] != 'service' and \
                    vals.get('procurement_type'):
                vals = self._compute_procurement_vals(vals)
                self._check_sellers(cr, uid, ids,
                                    vals['procurement_type'],
                                    context=context)
        res = super(product_template, self).write(cr, uid, ids,
                                                  vals, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        if vals['type'] != 'service' and vals.get('procurement_type'):
            vals = self._compute_procurement_vals(vals)
        return super(product_template, self).create(cr, uid, vals,
                                                    context=context)

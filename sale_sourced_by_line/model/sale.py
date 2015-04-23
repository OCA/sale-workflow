# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier, Yannick Vaucher
#    Copyright 2013-2015 Camptocamp SA
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

from openerp import models, api, fields
from openerp.osv import orm


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(self, cr, uid, order, line,
                                        group_id=False, context=None):
        values = super(SaleOrder, self)._prepare_order_line_procurement(
            cr, uid, order, line, group_id=group_id, context=context)
        if line.warehouse_id:
            values['warehouse_id'] = line.warehouse_id.id
        return values

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        vals = super(SaleOrder, self)._prepare_procurement_group_by_line(line)
        # for compatibility with sale_quotation_sourcing
        if line._get_procurement_group_key()[0] == 8:
            if line.warehouse_id:
                vals['name'] += '/' + line.warehouse_id.name
        return vals

    SO_STATES = {
        'cancel': [('readonly', True)],
        'progress': [('readonly', True)],
        'manual': [('readonly', True)],
        'shipping_except': [('readonly', True)],
        'invoice_except': [('readonly', True)],
        'done': [('readonly', True)],
    }

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        'Default Warehouse',
        states=SO_STATES,
        help="If no source warehouse is selected on line, "
             "this warehouse is used as default. ")


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        'Source Warehouse',
        help="If a source warehouse is selected, "
             "it will be used to define the route. "
             "Otherwise, it will get the warehouse of "
             "the sale order")

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        priority = 8
        key = super(SaleOrderLine, self)._get_procurement_group_key()
        # Check priority
        if key[0] >= priority:
            return key
        return (priority, self.warehouse_id.id)

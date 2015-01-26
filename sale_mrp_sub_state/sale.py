# -*- encoding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2015 AKRETION (http://www.akretion.com)
#   @author Chafique DELLI
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
from openerp.osv import orm


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    def write(self, cr, uid, ids, values, context=None):
        sale_obj = self.pool['sale.order']
        mrp_production = self.browse(cr, uid, ids[0], context=context)
        status_list = ['confirmed', 'ready', 'in_production', 'done']
        if 'state' in values:
            if mrp_production.sale_name and values['state'] in status_list:
                sale_ids = sale_obj.search(cr, uid, [
                    ('name', '=', mrp_production.sale_name),
                ], context=context)
                if sale_ids:
                    sale_obj.write(cr, uid, sale_ids, {
                        'sub_state': values['state'],
                    }, context=context)
        return super(MrpProduction, self).write(
            cr, uid, ids, values, context=context)


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def _get_sub_state_selection(self, cr, uid, context=None):
        selection = super(SaleOrder, self)._get_sub_state_selection(
            cr, uid, context=context)
        selection += [
            ('confirmed', 'Awaiting Raw Materials'),
            ('ready', 'Ready to Produce'),
            ('in_production', 'Production Started'),
            ('done', 'Production Done'),
        ]
        return selection

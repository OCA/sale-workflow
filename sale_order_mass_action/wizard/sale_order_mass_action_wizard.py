# -*- coding: utf-8 -*-
##############################################################################
#
#    Sale - Sale Order Mass Action module for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from openerp.osv import fields
from openerp.osv.orm import TransientModel


class SaleOrderMassActionWizard(TransientModel):
    _name = 'sale.order.mass.action.wizard'

    def _compute_confirmable_order_ids(self, cr, uid, context=None):
        so_obj = self.pool['sale.order']
        return so_obj.search(cr, uid, [
            ('id', 'in', context.get('active_ids', [])),
            ('state', '=', 'draft')], context=context)

    def _compute_finishable_order_ids(self, cr, uid, context=None):
        so_obj = self.pool['sale.order']
        return so_obj.search(cr, uid, [
            ('id', 'in', context.get('active_ids', [])),
            ('state', '=', 'progress')], context=context)

    def _default_confirmable_order_qty(self, cr, uid, context=None):
        return len(
            self._compute_confirmable_order_ids(cr, uid, context=context))

    def _default_finishable_order_qty(self, cr, uid, context=None):
        return len(
            self._compute_finishable_order_ids(cr, uid, context=context))

    _columns = {
        'confirmable_order_qty': fields.integer(
            string='Confirmable Order Quantity', readonly=True),
        'confirm': fields.boolean(
            'Confirm', help="""check this box if you want to"""
            """ confirm all the selected quotations."""),
        'finishable_order_qty': fields.integer(
            string='Finishable Order Quantity', readonly=True),
        'finish': fields.boolean(
            'Manually Set To Done', help="""check this box if you manually"""
            """ set to done selected orders."""),
    }

    _defaults = {
        'confirm': True,
        'confirmable_order_qty': _default_confirmable_order_qty,
        'finish': True,
        'finishable_order_qty': _default_finishable_order_qty,
    }

    def apply_button(self, cr, uid, ids, context=None):
        context = context or {}
        so_obj = self.pool['sale.order']
        wizard = self.browse(cr, uid, ids[0], context=context)
        if wizard.confirm:
            for so_id in self._compute_confirmable_order_ids(
                    cr, uid, context=context):
                so_obj.action_button_confirm(cr, uid, [so_id], context=context)
        if wizard.finish:
            so_ids = self._compute_finishable_order_ids(
                cr, uid, context=context)
            so_obj.write(cr, uid, so_ids, {'state': 'done'}, context=context)
        return True

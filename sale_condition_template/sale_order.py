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
from openerp.tools.translate import _


class SaleOrder(orm.Model):

    """Add text condition"""

    _inherit = "sale.order"
    _columns = {
        'condition_template1_id': fields.many2one(
            'base.condition_template',
            'Template Top conditions'),
        'condition_template2_id': fields.many2one(
            'base.condition_template',
            'Template Bottom conditions'),
        'note1': fields.html('Top conditions'),
        'note2': fields.html('Bottom conditions'),
    }

    def set_condition(self, cr, uid, cond_id, field_name, partner_id):
        if not cond_id:
            return {'value': {field_name: ''}}
        cond_obj = self.pool['base.condition_template']
        text = cond_obj.get_value(cr, uid, cond_id, partner_id)
        return {'value': {field_name: text}}

    def set_note1(self, cr, uid, so_id, cond_id, partner_id):
        return self.set_condition(cr, uid, cond_id, 'note1', partner_id)

    def set_note2(self, cr, uid, so_id, cond_id, partner_id):
        return self.set_condition(cr, uid, cond_id, 'note2', partner_id)

    def action_invoice_create(self, cr, user, order_id,
                              grouped=False,
                              states=['confirmed', 'done', 'exception'],
                              date_inv=False, context=None):
        # function is design to return only one id
        invoice_obj = self.pool['account.invoice']
        inv_id = super(SaleOrder, self).action_invoice_create(
            cr, user, order_id, grouped, states, date_inv, context=context)

        invoice = invoice_obj.browse(cr, user, inv_id, context=context)
        if isinstance(order_id, list):
            if len(order_id) > 1:
                raise orm.except_osv(
                    _('action_invoice_create can only receive one id'),
                    _('action_invoice_create can only receive one id'))

            order_id = order_id[0]
        order = self.browse(cr, user, order_id, context=context)
        inv_data = {'condition_template1_id': order.condition_template1_id.id,
                    'condition_template2_id': order.condition_template2_id.id,
                    'note1': order.note1,
                    'note2': order.note2}
        invoice.write(inv_data, context=context)
        return inv_id

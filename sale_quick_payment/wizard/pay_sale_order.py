# -*- coding: utf-8 -*-
##############################################################################
#
#    sale_quick_payment for OpenERP
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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
import openerp.addons.decimal_precision as dp


class pay_sale_order(orm.TransientModel):
    _name = 'pay.sale.order'
    _description = 'Wizard to generate a payment from the sale order'

    _columns = {
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'amount': fields.float('Amount',
                               digits_compute=dp.get_precision('Sale Price')),
        'date': fields.datetime('Payment Date'),
        'description': fields.char('Description', size=64),
    }

    def _get_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('active_id'):
            sale_obj = self.pool.get('sale.order')
            order = sale_obj.browse(cr, uid, context['active_id'],
                                    context=context)
            if order.payment_method_id:
                return order.payment_method_id.journal_id.id
        return False

    def _get_amount(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('active_id'):
            sale_obj = self.pool.get('sale.order')
            order = sale_obj.browse(cr, uid, context['active_id'],
                                    context=context)
            return order.residual
        return False

    _defaults = {
        'journal_id': _get_journal_id,
        'amount': _get_amount,
        'date': fields.datetime.now,
    }

    def pay_sale_order(self, cr, uid, ids, context=None):
        """ Pay the sale order """
        wizard = self.browse(cr, uid, ids[0], context=context)
        sale_obj = self.pool.get('sale.order')
        sale_obj.add_payment(cr, uid,
                             context['active_id'],
                             wizard.journal_id.id,
                             wizard.amount,
                             wizard.date,
                             description=wizard.description,
                             context=context)
        return {'type': 'ir.actions.act_window_close'}

    def pay_sale_order_and_confirm(self, cr, uid, ids, context=None):
        """ Pay the sale order """
        self.pay_sale_order(cr, uid, ids, context=context)
        sale_obj = self.pool.get('sale.order')
        return sale_obj.action_button_confirm(cr, uid,
                                              [context['active_id']],
                                              context=context)

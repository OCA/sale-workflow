# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    Magentoerpconnect for OpenERP                                              #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################


from openerp.osv.orm import TransientModel
from openerp.osv import fields
import decimal_precision as dp
from datetime import datetime

class pay_sale_order(TransientModel):
    _name = 'pay.sale.order'
    _description = 'Wizard to generate a payment from the sale order'

    _columns = {
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Sale Price')),
        'date': fields.datetime('Payment Date'),
        }

    def _get_journal_id(self, cr, uid, args):
        if args.get('payment_method_id'):
            payment_method = self.pool.get('payment.method').browse(cr, uid, args['payment_method_id'])
            return payment_method.journal_id.id
        return False

    def _get_amount(self, cr, uid, args):
        if args.get('amount_total'):
            return args['amount_total']
        return False

    _defaults = {
        'journal_id': _get_journal_id,
        'amount': _get_amount,
        'date': fields.datetime.now,
    }

    def pay_sale_order(self, cr, uid, ids, context=None):
        """
        Pay the sale order
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of account chart’s IDs
        @return: dictionary of Product list window for a given attributs set
        """
        for wizard in self.browse(cr, uid, ids, context=context):
            self.pool.get('sale.order').pay_sale_order(cr, uid, context['active_id'], wizard.journal_id.id, wizard.amount, wizard.date, context=context)
        return {'type': 'ir.actions.act_window_close'}

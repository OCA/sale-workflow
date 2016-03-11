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

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class PaySaleOrder(models.TransientModel):
    _name = 'pay.sale.order'
    _description = 'Wizard to generate a payment from the sale order'

    @api.model
    def _default_journal_id(self):
        context = self.env.context
        if not context.get('active_id'):
            return False
        order = self.env['sale.order'].browse(context['active_id'])
        if order.payment_method_id:
            return order.payment_method_id.journal_id.id
        return False

    journal_id = fields.Many2one('account.journal', 'Journal',
                                 default=_default_journal_id)

    @api.model
    def _default_amount(self):
        context = self.env.context
        if not context.get('active_id'):
            return False
        return self.env['sale.order'].browse(context['active_id']).residual

    amount = fields.Float('Amount', digits=dp.get_precision('Sale Price'),
                          default=_default_amount)

    date = fields.Datetime('Payment Date', default=fields.Datetime.now)

    description = fields.Char('Description', size=64)

    @api.multi
    def pay_sale_order(self):
        """ Pay the sale order """
        self.ensure_one()
        order = self.env['sale.order'].browse(self.env.context['active_id'])
        order.add_payment(self.journal_id.id,
                          self.amount,
                          date=self.date,
                          description=self.description)
        return True

    @api.multi
    def pay_sale_order_and_confirm(self):
        """ Pay the sale order """
        self.ensure_one()
        self.pay_sale_order()
        order = self.env['sale.order'].browse(self.env.context['active_id'])
        return order.action_button_confirm()

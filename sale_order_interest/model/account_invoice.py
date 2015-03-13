# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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

from openerp import models, fields, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('payment_term')
    def onchange_payment_term_add_interest_line(self):
        line_model = self.env['account.invoice.line']
        interest_line = self._get_interest_line()
        if not self.payment_term:
            if interest_line:
                self.invoice_line -= interest_line
        else:
            interest_amount = self.get_interest_value()
            values = self._prepare_interest_line(interest_amount)

            if interest_line:
                if interest_amount:
                    interest_line.write(values)
                else:
                    self.invoice_line -= interest_line
            elif interest_amount:
                self.invoice_line += line_model.new(values)

    @api.multi
    def _prepare_interest_line(self, interest_amount):
        product = self.env.ref('account_invoice_interest.'
                               'product_product_invoice_interest')
        values = {'quantity': 1,
                  'invoice_id': self.id,
                  'product_id': product.id,
                  'interest_line': True,
                  'sequence': 99999,
                  }
        onchanged = self.env['account.invoice.line'].product_id_change(
            product.id,
            product.uom_id.id,
            qty=1,
            name='',
            partner_id=self.partner_id.id,
            fposition_id=self.fiscal_position.id,
            price_unit=interest_amount,
            currency_id=self.currency_id.id,
            company_id=self.company_id.id)
        values.update(onchanged['value'])
        values['price_unit'] = interest_amount
        return values

    @api.multi
    def get_interest_value(self):
        self.ensure_one()
        term = self.payment_term
        if not term:
            return 0.
        if not any(line.interest_rate for line in term.line_ids):
            return 0.
        interest_line = self._get_interest_line()
        # deduce the existing interest line
        # XXX does not include the taxes, so if the interest line has
        # taxes, the amount will include the tax of the interest line
        interest_amount = interest_line.price_subtotal
        values = term.compute_interest(self.amount_total - interest_amount,
                                       date_ref=self.date_invoice)
        return sum(interest for __, __, interest in values)

    @api.multi
    def _get_interest_line(self):
        for line in self.invoice_line:
            if line.interest_line:
                return line
        return self.env['account.invoice.line'].browse()

    @api.multi
    def update_interest_line(self):
        interest_line = self._get_interest_line()
        interest_amount = self.get_interest_value()
        values = self._prepare_interest_line(interest_amount)

        if interest_line:
            if interest_amount:
                interest_line.write(values)
            else:
                interest_line.unlink()
        elif interest_amount:
            self.env['account.invoice.line'].create(values)

    @api.multi
    def check_interest_line(self):
        self.ensure_one()
        interest_amount = self.get_interest_value()
        currency = self.currency_id

        interest_line = self._get_interest_line()
        current_amount = interest_line.price_unit

        if currency.compare_amounts(current_amount, interest_amount) != 0:
            raise exceptions.Warning(
                _('Interest amount differs. Click on "(update interests)" '
                  'next to the payment terms.')
            )

    @api.multi
    def action_move_create(self):
        result = super(AccountInvoice, self).action_move_create()
        self.check_interest_line()
        return result


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    interest_line = fields.Boolean()

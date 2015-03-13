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

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _prepare_interest_line(self, interest_amount):
        product = self.env.ref('account_invoice_interest.'
                               'product_product_invoice_interest')
        values = {'quantity': 1,
                  'invoice_id': self.id,
                  'product_id': product.id,
                  'interest_line': True
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
        values = term.compute_interest(self.amount_total,
                                       date_ref=self.date_invoice)
        return sum(interest for __, __, interest in values)

    @api.multi
    def update_interest_line(self):
        interest_line = None
        for line in self.invoice_line:
            if line.interest_line:
                interest_line = line

        interest_amount = self.get_interest_value()
        values = self._prepare_interest_line(interest_amount)

        if interest_line:
            if interest_amount:
                interest_line.write(values)
            else:
                interest_line.unlink()
        elif interest_amount:
            self.env['account.invoice.line'].create(values)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    interest_line = fields.Boolean()

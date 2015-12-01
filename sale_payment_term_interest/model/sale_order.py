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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_interest_line(self, interest_amount):
        self.ensure_one()
        product = self.env.ref('sale_payment_term_interest.'
                               'product_product_sale_order_interest')
        values = {'product_uom_qty': 1,
                  'order_id': self.id,
                  'product_id': product.id,
                  'interest_line': True,
                  'sequence': 99999,
                  }
        onchanged = self.env['sale.order.line'].product_id_change(
            self.pricelist_id.id,
            product.id,
            qty=1,
            uom=product.uom_id.id,
            partner_id=self.partner_id.id,
            fiscal_position=self.fiscal_position.id)
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
        line = self._get_interest_line()
        if line:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price,
                                            line.product_uom_qty,
                                            product=line.product_id,
                                            partner=self.partner_id)
            # remove the interest value from the total if there is a value yet
            current_interest = taxes['total_included']
        else:
            current_interest = 0.
        interest = term.compute_total_interest(
            self.amount_total - current_interest,
        )
        return interest

    @api.multi
    def _get_interest_line(self):
        for line in self.order_line:
            if line.interest_line:
                return line
        return self.env['sale.order.line'].browse()

    @api.multi
    def update_interest_line(self):
        for order in self:
            interest_line = order._get_interest_line()
            interest_amount = order.get_interest_value()
            values = order._prepare_interest_line(interest_amount)

            if interest_line:
                if interest_amount:
                    values.pop('name', None)  # keep the current name
                    interest_line.write(values)
                else:
                    interest_line.unlink()
            elif interest_amount:
                self.env['sale.order.line'].create(values)

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
    def action_button_confirm(self):
        result = super(SaleOrder, self).action_button_confirm()
        self.check_interest_line()
        return result

    @api.model
    def create(self, vals):
        record = super(SaleOrder, self).create(vals)
        record.update_interest_line()
        return record

    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        self.update_interest_line()
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    interest_line = fields.Boolean()

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

from __future__ import division

from datetime import datetime
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
from openerp import models, fields, api
from openerp.tools.float_utils import float_round as round, float_compare


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    interest_min = fields.Float(
        string='Minimum Interest Amount',
        digits=dp.get_precision('Account'),
        help="The minimum amount of interest added to a sales "
             "order.")

    @api.multi
    def compute_total_interest(self, value):
        self.ensure_one()
        values = self.compute_interest(value)
        interest = sum(interest for __, __, interest in values)
        precision_model = self.env['decimal.precision']
        precision = precision_model.precision_get('Account')
        compare = float_compare(interest,
                                self.interest_min,
                                precision_digits=precision)
        if compare == -1:  # interest < interest_min
            return self.interest_min
        else:
            return interest

    @api.multi
    def compute_interest(self, value, date_ref=False):
        if date_ref:
            date_ref = fields.Date.from_string(date_ref)
        else:
            date_ref = datetime.today().date()

        amount = value
        result = []

        lines_total = 0.0
        precision_model = self.env['decimal.precision']
        # The computation of the amount for each term is the exact same
        # than the one in 'account_payment_term.compute()', this is
        # required to ensure that the interest fees are based on the
        # same amounts. This is why the 'account' precision is used:
        # this is the one used in 'account_payment_term.compute()'.
        prec = precision_model.precision_get('Account')
        for line in self.line_ids:
            if line.value == 'fixed':
                line_amount = round(line.value_amount, precision_digits=prec)
            elif line.value == 'procent':
                line_amount = round(value * line.value_amount,
                                    precision_digits=prec)
            elif line.value == 'balance':
                line_amount = round(amount, prec)
            if not line_amount:
                continue
            next_date = date_ref + relativedelta(days=line.days)
            if line.days2 < 0:
                # Getting 1st of next month
                next_first_date = next_date + relativedelta(day=1,
                                                            months=1)
                next_date = (next_first_date +
                             relativedelta(days=line.days2))
            if line.days2 > 0:
                next_date += relativedelta(day=line.days2, months=1)
            interest = 0.0
            if line.interest_rate:
                days = (next_date - date_ref).days
                rate = line.interest_rate / 100 / (12 * 30)  # %/(months*days)
                interest = line_amount * rate * days
            result.append((fields.Date.to_string(next_date),
                           line_amount,
                           interest))
            amount -= line_amount
            lines_total += line_amount

        dist = round(value - lines_total, precision_digits=prec)
        if dist:
            result.append((fields.Date.today(), dist, 0.0))
        return result


class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    interest_rate = fields.Float(
        string='Interest Rate',
        digits=dp.get_precision('Payment Term'),
        help="The annual interest rate applied on a sales order. "
             "Value between 0 and 100.\n"
             "The interest is computed as: "
             "'Amount * (Interest Rate / 100 / "
             " (12 months * 30 days)) * Term Days'")

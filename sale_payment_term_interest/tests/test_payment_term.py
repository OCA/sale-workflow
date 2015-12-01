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

from operator import itemgetter
from openerp.tests import common
from openerp.tools.float_utils import float_round as round


class TestPaymentTerm(common.TransactionCase):

    def setUp(self):
        super(TestPaymentTerm, self).setUp()
        self.term = self.env['account.payment.term'].create({
            'name': 'test',
            'interest_min': 2.,
        })
        self.env['account.payment.term.line'].create({
            'payment_id': self.term.id,
            'value': 'procent',
            'value_amount': 0.3333,
            'days': 10,
            'interest_rate': 0.0,
        })
        self.env['account.payment.term.line'].create({
            'payment_id': self.term.id,
            'value': 'procent',
            'value_amount': 0.3333,
            'days': 40,
            'interest_rate': 15,  # annual interest
        })
        self.env['account.payment.term.line'].create({
            'payment_id': self.term.id,
            'value': 'balance',
            'days': 70,
            'interest_rate': 15,  # annual interest
        })
        precision_model = self.env['decimal.precision']
        self.precision = precision_model.precision_get('Account')

    def test_interest_lines(self):
        total_amount = remaining_amount = 469.35
        terms = self.term.compute_interest(remaining_amount,
                                           date_ref='2015-03-13')
        self.assertEquals(len(terms), 3)
        terms = sorted(terms, key=itemgetter(0))
        line1, line2, line3 = terms

        precision = self.precision

        term_amount = total_amount * 0.3333
        # Odoo rounds the remaining amount between each term
        remaining_amount -= round(term_amount, precision_digits=precision)
        self.assertAlmostEqual(line1[1], term_amount,
                               places=precision)
        self.assertAlmostEqual(line1[2], 0.0,
                               places=precision)

        remaining_amount -= round(term_amount, precision_digits=precision)
        self.assertAlmostEqual(line2[1], term_amount,
                               places=precision)
        self.assertAlmostEqual(
            line2[2],
            (term_amount *  # due amount
             (15 / 100 /  # annual interest rate
              (12 * 30)  # (months / days) get a daily rate
              ) * 40  # multiply by the number of term days
             ),
            places=precision)

        self.assertAlmostEqual(line3[1], remaining_amount,
                               places=precision)
        self.assertAlmostEqual(
            line3[2],
            (remaining_amount *  # due amount
             (15 / 100 /  # annual interest rate
              (12 * 30)  # (months / days) get a daily rate
              ) * 70  # multiply by the number of term days
             ),
            places=precision)

    def test_total_interest(self):
        total_amount = 469.35
        interest = self.term.compute_total_interest(total_amount)
        expected = (
            # ((term amount) * rate / (number of days in one year) *
            # number of days)
            (((469.35 * 0.3333) * 0.15 / (12 * 30)) * 40) +
            (((469.35 * 0.3333) * 0.15 / (12 * 30)) * 70)
        )
        self.assertAlmostEqual(interest, expected, places=self.precision)

    def test_total_interest_min(self):
        total_amount = 469.35
        self.term.interest_min = interest_min = 20.
        interest = self.term.compute_total_interest(total_amount)
        self.assertAlmostEqual(interest, interest_min, places=self.precision)

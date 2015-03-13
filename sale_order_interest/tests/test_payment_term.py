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

from operator import itemgetter
from openerp.tests import common


class TestPaymentTerm(common.TransactionCase):

    def test_interest(self):
        term = self.env['account.payment.term'].create({'name': 'test'})
        self.env['account.payment.term.line'].create({
            'payment_id': term.id,
            'value': 'procent',
            'value_amount': 0.3333,
            'days': 10,
            'interest_rate': 0.0,
        })
        self.env['account.payment.term.line'].create({
            'payment_id': term.id,
            'value': 'procent',
            'value_amount': 0.3333,
            'days': 40,
            'interest_rate': 0.041666,
        })
        self.env['account.payment.term.line'].create({
            'payment_id': term.id,
            'value': 'balance',
            'days': 70,
            'interest_rate': 0.041666,
        })
        terms = term.compute_interest(469.35, date_ref='2015-03-13')
        self.assertEquals(len(terms), 3)
        terms = sorted(terms, key=itemgetter(0))
        line1, line2, line3 = terms
        self.assertAlmostEqual(line1[1], 156.43)
        self.assertAlmostEqual(line1[2], 0.0)

        self.assertAlmostEqual(line2[1], 156.43)
        self.assertAlmostEqual(line2[2], 2.60712495)

        self.assertAlmostEqual(line3[1], 156.49)
        self.assertAlmostEqual(line3[2], 4.56421864)

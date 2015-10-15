# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Opener B.V. (<https://opener.am>)
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
from openerp.tests.common import TransactionCase


class TestSalePartnerIncoterm(TransactionCase):
    def test_sale_partner_incoterm(self):
        """ Check that the customer's default incoterm is retrieved in the \
sales order's onchange """
        customer = self.env['res.partner'].search(
            [('customer', '=', True)], limit=1)
        incoterm = self.env['stock.incoterms'].search([], limit=1)
        customer.write({'sale_incoterm_id': incoterm.id})
        res = self.env['sale.order'].onchange_partner_id(customer.id)['value']
        self.assertEqual(res['incoterm'], incoterm.id)

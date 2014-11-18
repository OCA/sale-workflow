#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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
from openerp.tests.common import TransactionCase


class TestDropshippingSkipCheck(TransactionCase):
    def test_dropshipping_sale_can_always_be_delivered(self):
        source_loc = self.env['stock.location'].new({'usage': 'supplier'})
        order_line = self.env['sale.order.line'].new()
        order_line._get_line_location = lambda: source_loc

        self.assertIs(True, order_line.can_command_at_delivery_date())

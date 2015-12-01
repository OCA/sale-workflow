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


class TestPropagateOwner(TransactionCase):

    def test_it_propagates_empty_owner_to_the_move(self):
        self.so.action_button_confirm()

        self.assertEqual(1, len(self.so.picking_ids))
        self.assertFalse(self.so.picking_ids.move_lines[0].restrict_partner_id)

    def test_it_propagates_owner_to_the_move(self):
        self.sol.stock_owner_id = self.partner.id

        self.so.action_button_confirm()

        self.assertEqual(1, len(self.so.picking_ids))
        self.assertEqual(self.so.picking_ids.move_lines[0].restrict_partner_id,
                         self.partner)

    def setUp(self):
        super(TestPropagateOwner, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')

        # this product already has some stock with no owner in demo data
        product = self.env.ref('product.product_product_6')
        self.env['stock.quant'].create({
            'qty': 5000,
            'location_id': self.ref('stock.stock_location_stock'),
            'product_id': product.id,
            'owner_id': self.partner.id,
        })

        self.so = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
        })
        self.sol = self.env['sale.order.line'].create({
            'name': '/',
            'order_id': self.so.id,
            'product_id': product.id,
        })

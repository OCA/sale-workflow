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


class TestIntSaleToReservation(TransactionCase):
    """Integration tests of the propagation of the owner.

    Here we check the whole trip from the quotation line to the reservation of
    the stock.

    """

    def test_one_line_with_owner_reserves_its_stock(self):
        self.sol.stock_owner_id = self.owner1
        self.so.action_button_confirm()

        picking = self.so.picking_ids
        picking.action_assign()
        self.assertEqual('assigned', picking.state)
        self.assertEqual(self.owner1,
                         picking.move_lines.reserved_quant_ids.owner_id)

    def test_one_line_without_owner_reserves_my_stock(self):
        self.so.action_button_confirm()

        picking = self.so.picking_ids
        picking.action_assign()
        self.assertEqual('assigned', picking.state)
        self.assertEqual(self.my_partner,
                         picking.move_lines.reserved_quant_ids.owner_id)

    def test_two_lines_one_with_owner_reserves_correct_stock(self):
        self.sol.copy({'stock_owner_id': self.owner1.id})
        self.so.action_button_confirm()

        picking = self.so.picking_ids
        picking.action_assign()
        self.assertEqual('assigned', picking.state)

        quant_owners = set([move.reserved_quant_ids.owner_id
                            for move in picking.move_lines])

        self.assertEqual(set([self.my_partner, self.owner1]), quant_owners)

    def test_one_line_without_owner_insufficient_stock_respects_stock(self):
        self.sol.product_uom_qty = 6000
        self.so.action_button_confirm()

        picking = self.so.picking_ids
        picking.action_assign()
        self.assertEqual('partially_available', picking.state)
        self.assertEqual(self.my_partner,
                         picking.move_lines.reserved_quant_ids.owner_id)

    def setUp(self):
        super(TestIntSaleToReservation, self).setUp()

        self.owner1 = self.env.ref('base.res_partner_1')
        self.owner2 = self.env.ref('base.res_partner_2')
        customer = self.env.ref('base.res_partner_3')
        self.my_partner = self.env.user.company_id.partner_id

        # this product has no stock in demo data
        product = self.env.ref('product.product_product_36')

        quant = self.env['stock.quant'].create({
            'qty': 5000,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': product.id,
        })

        quant.copy({'owner_id': self.owner1.id})
        quant.copy({'owner_id': self.owner2.id})

        self.so = self.env['sale.order'].create({
            'partner_id': customer.id,
        })
        self.sol = self.env['sale.order.line'].create({
            'name': '/',
            'order_id': self.so.id,
            'product_id': product.id,
        })

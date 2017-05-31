# -*- coding: utf-8 -*-
# © 2015-2015 Yannick Vaucher, Leonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestIntSaleToReservation(TransactionCase):
    """Integration tests of the propagation of the owner.

    Here we check the whole trip from the quotation line to the reservation of
    the stock.

    """

    def test_one_line_with_owner_reserves_its_stock(self):
        self.sol.stock_owner_id = self.owner1
        self.so.action_confirm()

        picking = self.so.picking_ids
        picking.action_assign()
        self.assertEqual('assigned', picking.state)
        self.assertEqual(self.owner1,
                         picking.move_lines.reserved_quant_ids.owner_id)

    def test_one_line_without_owner_reserves_my_stock(self):
        self.so.action_confirm()

        picking = self.so.picking_ids
        picking.action_assign()
        self.assertEqual('assigned', picking.state)
        self.assertEqual(self.my_partner,
                         picking.move_lines.reserved_quant_ids.owner_id)

    def test_two_lines_one_with_owner_reserves_correct_stock(self):
        self.sol.copy(
            {'order_id': self.sol.order_id.id,
             'stock_owner_id': self.owner1.id})
        self.so.action_confirm()

        picking = self.so.picking_ids
        picking.action_assign()
        self.assertEqual('assigned', picking.state)

        quant_owners = set([move.reserved_quant_ids.owner_id
                            for move in picking.move_lines])

        self.assertEqual(set([self.my_partner, self.owner1]), quant_owners)

    def test_one_line_without_owner_insufficient_stock_respects_stock(self):
        self.sol.product_uom_qty = 6000
        self.so.action_confirm()

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
        product = self.env.ref('product.product_product_8')

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

# -*- coding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2015  Agile Business Group                              #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU Affero General Public License as        #
# published by the Free Software Foundation, either version 3 of the    #
# License, or (at your option) any later version.                       #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU Affero General Public Licensefor more details.                    #
#                                                                       #
# You should have received a copy of the                                #
# GNU Affero General Public License                                     #
# along with this program.  If not, see <http://www.gnu.org/licenses/>. #
#                                                                       #
#########################################################################
import openerp.tests.common as test_common


class TestSaleOrderLotSelection(test_common.SingleTransactionCase):
    def setUp(self):
        """Set up a sale order a particular lot.

        I confirm it, transfer the delivery order and check lot on picking

        """
        super(TestSaleOrderLotSelection, self).setUp()
        product_11 = self.env.ref('product.product_product_11')
        self.lot = self.env['stock.production.lot'].create(
            {
                'name': "0000010",
                'product_id': product_11.id
            })
        self.order = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.sol1 = self.env['sale.order.line'].create({
            'name': 'sol1',
            'order_id': self.order.id,
            'lot_id': self.lot.id,
            'product_id': product_11.id,
        })

    def test_order_confirm_and_picking_transfer(self):
        self.order.action_button_confirm()
        picking = self.order.picking_ids
        picking.action_assign()
        picking.do_enter_transfer_details()
        wiz = self.env['stock.transfer_details'].search([
            ['picking_id', '=', picking.id]])
        wiz.do_detailed_transfer()
        self.assertEqual(self.lot,
                         picking.move_lines.lot_ids)

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
from openerp.exceptions import Warning


class TestSaleOrderLotSelection(test_common.SingleTransactionCase):

    def setUp(self):
        """
        Set up a sale order a particular lot.

        I confirm it, transfer the delivery order and check lot on picking

        Set up a sale order with two lines with different products and lots.

        I confirm it, transfer the delivery order and check lots on picking

        """
        super(TestSaleOrderLotSelection, self).setUp()
        self.product_57 = self.env.ref('product.product_product_57')
        self.product_46 = self.env.ref('product.product_product_46')
        self.product_12 = self.env.ref('product.product_product_12')
        self.product_57.write({'tracking': 'lot', 'type': 'product'})
        self.product_46.write({'tracking': 'lot', 'type': 'product'})
        self.product_12.write({'tracking': 'lot', 'type': 'product'})
        self.supplier_location = self.env.ref(
            'stock.stock_location_suppliers')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.product_model = self.env['product.product']

    def _stock_quantity(self, product, lot, location):
        return product.with_context({
            'lot_id': lot.id,
            'location': location.id,
            })._product_available()

    def test_sale_order_lot_selection(self):
        # make products enter
        picking_in = self.env['stock.picking'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'picking_type_id': self.env['ir.model.data'].xmlid_to_res_id(
                'stock.picking_type_in'),
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id})
        self.env['stock.move'].create({
            'name': self.product_57.name,
            'product_id': self.product_57.id,
            'product_uom_qty': 1,
            'product_uom': self.product_57.uom_id.id,
            'picking_id': picking_in.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id})
        self.env['stock.move'].create({
            'name': self.product_12.name,
            'product_id': self.product_12.id,
            'product_uom_qty': 1,
            'product_uom': self.product_12.uom_id.id,
            'picking_id': picking_in.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id})
        self.env['stock.move'].create({
            'name': self.product_46.name,
            'product_id': self.product_46.id,
            'product_uom_qty': 2,
            'product_uom': self.product_46.uom_id.id,
            'picking_id': picking_in.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id})
        for move in picking_in.move_lines:
            self.assertEqual(move.state, 'draft', 'Wrong state of move line.')
        picking_in.action_confirm()
        for move in picking_in.move_lines:
            self.assertEqual(
                move.state, 'assigned', 'Wrong state of move line.')
        for ops in picking_in.pack_operation_ids:
            if ops.product_id == self.product_57:
                ops.write({
                    'pack_lot_ids': [(0, 0, {
                        'lot_name': '0000010',
                        'qty': ops.product_qty,
                        'qty_todo': ops.product_qty
                        })],
                    'qty_done': ops.product_qty
                    })
            if ops.product_id == self.product_46:
                ops.write({
                    'pack_lot_ids': [(0, 0, {
                        'lot_name': '0000011',
                        'qty': ops.product_qty,
                        'qty_todo': ops.product_qty
                        })],
                    'qty_done': ops.product_qty
                    })
            if ops.product_id == self.product_12:
                ops.write({
                    'pack_lot_ids': [(0, 0, {
                        'lot_name': '0000012',
                        'qty': ops.product_qty,
                        'qty_todo': ops.product_qty
                        })],
                    'qty_done': ops.product_qty
                    })
        picking_in.do_new_transfer()
        lot_obj = self.env['stock.production.lot']
        self.lot10 = lot_obj.search([('name', '=', '0000010'),
                                     ('product_id', '=', self.product_57.id)])
        self.lot11 = lot_obj.search([('name', '=', '0000011'),
                                     ('product_id', '=', self.product_46.id)])
        self.lot12 = lot_obj.search([('name', '=', '0000012'),
                                     ('product_id', '=', self.product_12.id)])
        # check quantities
        lot10_qty = self._stock_quantity(
            self.product_57, self.lot10, self.stock_location)
        self.assertEqual(lot10_qty[self.product_57.id]['qty_available'], 1)
        lot11_qty = self._stock_quantity(
            self.product_46, self.lot11, self.stock_location)
        self.assertEqual(lot11_qty[self.product_46.id]['qty_available'], 2)
        lot12_qty = self._stock_quantity(
            self.product_12, self.lot12, self.stock_location)
        self.assertEqual(lot12_qty[self.product_12.id]['qty_available'], 1)

        # create order
        self.order1 = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.sol1 = self.env['sale.order.line'].create({
            'name': 'sol1',
            'order_id': self.order1.id,
            'lot_id': self.lot10.id,
            'product_id': self.product_57.id,
            'product_uom_qty': 1,
        })
        self.order2 = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.sol2a = self.env['sale.order.line'].create({
            'name': 'sol2a',
            'order_id': self.order2.id,
            'lot_id': self.lot11.id,
            'product_id': self.product_46.id,
            'product_uom_qty': 1,
        })
        self.sol2b = self.env['sale.order.line'].create({
            'name': 'sol2b',
            'order_id': self.order2.id,
            'lot_id': self.lot12.id,
            'product_id': self.product_12.id,
            'product_uom_qty': 1,
        })
        self.order3 = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.sol3 = self.env['sale.order.line'].create({
            'name': 'sol_test_1',
            'order_id': self.order3.id,
            'lot_id': self.lot10.id,
            'product_id': self.product_57.id,
            'product_uom_qty': 1,
        })
        self.order4 = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.sol4 = self.env['sale.order.line'].create({
            'name': 'sol4',
            'order_id': self.order4.id,
            'lot_id': self.lot11.id,
            'product_id': self.product_46.id,
            'product_uom_qty': 2,
        })

        # confirm orders
        self.order1.action_confirm()
        picking = self.order1.picking_ids
        picking.action_assign()
        picking.pack_operation_ids.pack_lot_ids.do_plus()
        picking.do_new_transfer()
        for pack in picking.pack_operation_ids:
            if pack.product_id.id == self.product_57.id:
                self.assertEqual(pack.pack_lot_ids.lot_id, self.lot10)

        # also test on_change for order3
        onchange_res = self.sol3._onchange_product_id_set_lot_domain()
        self.assertEqual(onchange_res['domain']['lot_id'], [('id', 'in', [])])
        # put back the lot because it is removed by onchange
        self.sol3.lot_id = self.lot10.id

        # I'll try to confirm it to check lot reservation:
        # lot10 was delivered by order1
        with self.assertRaises(Warning):
            self.order3.action_confirm()

        # also test on_change for order2
        onchange_res = self.sol2a._onchange_product_id_set_lot_domain()
        self.assertEqual(
            onchange_res['domain']['lot_id'], [('id', 'in', [self.lot11.id])])
        # onchange remove lot_id, we put it back
        self.sol2a.lot_id = self.lot11.id
        self.order2.action_confirm()
        picking = self.order2.picking_ids
        picking.action_assign()
        for pack_op in picking.pack_operation_ids:
            pack_op.pack_lot_ids.do_plus()
        picking.do_new_transfer()
        lot11_found = False
        lot12_found = False
        for pack in picking.pack_operation_ids:
            if pack.product_id.id == self.product_46.id:
                self.assertEqual(pack.pack_lot_ids.lot_id, self.lot11)
                lot11_found = True
            else:
                self.assertEqual(pack.pack_lot_ids.lot_id, self.lot12)
                lot12_found = True
        self.assertTrue(lot11_found)
        self.assertTrue(lot12_found)

        # check quantities
        lot10_qty = self._stock_quantity(
            self.product_57, self.lot10, self.stock_location)
        self.assertEqual(lot10_qty[self.product_57.id]['qty_available'], 0)
        lot11_qty = self._stock_quantity(
            self.product_46, self.lot11, self.stock_location)
        self.assertEqual(lot11_qty[self.product_46.id]['qty_available'], 1)
        lot12_qty = self._stock_quantity(
            self.product_12, self.lot12, self.stock_location)
        self.assertEqual(lot12_qty[self.product_12.id]['qty_available'], 0)
        # I'll try to confirm it to check lot reservation:
        # lot11 has 1 availability and order4 has quantity 2
        with self.assertRaises(Warning):
            self.order4.action_confirm()

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
        self.product_14 = self.env.ref('product.product_product_14')
        self.product_13 = self.env.ref('product.product_product_13')
        self.product_12 = self.env.ref('product.product_product_12')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.product_model = self.env['product.product']

    def _stock_quantity(self, product, lot, location):
        return product.with_context({
            'lot_id': lot.id,
            'location': location.id,
            })._product_available()

    def test_sale_order_lot_selection(self):
        self.lot10 = self.env['stock.production.lot'].create(
            {
                'name': "0000010",
                'product_id': self.product_14.id
            })
        self.lot11 = self.env['stock.production.lot'].create(
            {
                'name': "0000011",
                'product_id': self.product_13.id
            })
        self.lot12 = self.env['stock.production.lot'].create(
            {
                'name': "0000012",
                'product_id': self.product_12.id
            })

        self.order1 = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.sol1 = self.env['sale.order.line'].create({
            'name': 'sol1',
            'order_id': self.order1.id,
            'lot_id': self.lot10.id,
            'product_id': self.product_14.id,
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
            'product_id': self.product_13.id,
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
            'product_id': self.product_14.id,
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
            'product_id': self.product_13.id,
            'product_uom_qty': 2,
        })

        # make products enter
        picking_in = self.env['stock.picking'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'picking_type_id': self.env['ir.model.data'].xmlid_to_res_id(
                'stock.picking_type_in')})
        self.env['stock.move'].create({
            'name': self.product_14.name,
            'product_id': self.product_14.id,
            'product_uom_qty': 1,
            'product_uom': self.product_14.uom_id.id,
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
            'name': self.product_13.name,
            'product_id': self.product_13.id,
            'product_uom_qty': 2,
            'product_uom': self.product_13.uom_id.id,
            'picking_id': picking_in.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id})
        for move in picking_in.move_lines:
            self.assertEqual(move.state, 'draft', 'Wrong state of move line.')
        picking_in.action_confirm()
        for move in picking_in.move_lines:
            self.assertEqual(
                move.state, 'assigned', 'Wrong state of move line.')
        picking_in.do_prepare_partial()
        pick_wizard = self.env['stock.transfer_details'].with_context({
            'active_model': 'stock.picking',
            'active_ids': [picking_in.id],
            'active_id': picking_in.id,
            'default_picking_type_id': picking_in.id}).create({
                'picking_id': picking_in.id})
        for item in pick_wizard.item_ids:
            if item.product_id == self.product_14:
                item.lot_id = self.lot10
            if item.product_id == self.product_13:
                item.lot_id = self.lot11
            if item.product_id == self.product_12:
                item.lot_id = self.lot12
        pick_wizard.do_detailed_transfer()

        # check quantities
        lot10_qty = self._stock_quantity(
            self.product_14, self.lot10, self.stock_location)
        self.assertEqual(lot10_qty[self.product_14.id]['qty_available'], 1)
        lot11_qty = self._stock_quantity(
            self.product_13, self.lot11, self.stock_location)
        self.assertEqual(lot11_qty[self.product_13.id]['qty_available'], 2)
        lot12_qty = self._stock_quantity(
            self.product_12, self.lot12, self.stock_location)
        self.assertEqual(lot12_qty[self.product_12.id]['qty_available'], 1)

        # confirm orders
        self.order1.action_button_confirm()
        picking = self.order1.picking_ids
        picking.action_assign()
        picking.do_enter_transfer_details()
        wiz = self.env['stock.transfer_details'].search([
            ['picking_id', '=', picking.id]])
        wiz.do_detailed_transfer()
        for pack in picking.pack_operation_ids:
            if pack.product_id.id == self.product_14.id:
                self.assertEqual(pack.lot_id, self.lot10)

        # also test on_change for order3
        onchange_res = self.registry(
            'sale.order.line'
        ).product_id_change_with_wh(
            self.cr, self.uid, [], self.order3.pricelist_id.id,
            self.sol3.product_id.id,
            qty=self.sol3.product_uom_qty,
            uom=self.sol3.product_uom.id, qty_uos=0, uos=False,
            name='', partner_id=self.order3.partner_id.id,
            lang=False, update_tax=True, date_order=self.order3.date_order,
            packaging=False, fiscal_position=False, flag=False,
            warehouse_id=self.order3.warehouse_id.id,
            context=self.env.context)
        self.assertEqual(onchange_res['domain']['lot_id'], [('id', 'in', [])])

        # I'll try to confirm it to check lot reservation:
        # lot10 was delivered by order1
        with self.assertRaises(Warning):
            self.order3.action_button_confirm()

        # also test on_change for order2
        onchange_res = self.registry(
            'sale.order.line'
        ).product_id_change_with_wh(
            self.cr, self.uid, [], self.order2.pricelist_id.id,
            self.sol2a.product_id.id, qty=self.sol2a.product_uom_qty,
            uom=self.sol2a.product_uom.id, qty_uos=0, uos=False, name='',
            partner_id=self.order2.partner_id.id,
            lang=False, update_tax=True, date_order=self.order2.date_order,
            packaging=False, fiscal_position=False, flag=False,
            warehouse_id=self.order2.warehouse_id.id, context=self.env.context)
        self.assertEqual(
            onchange_res['domain']['lot_id'], [('id', 'in', [self.lot11.id])])

        self.order2.action_button_confirm()
        picking = self.order2.picking_ids
        picking.action_assign()
        picking.do_enter_transfer_details()
        wiz = self.env['stock.transfer_details'].search([
            ['picking_id', '=', picking.id]])
        wiz.do_detailed_transfer()
        lot11_found = False
        lot12_found = False
        for pack in picking.pack_operation_ids:
            if pack.product_id.id == self.product_13.id:
                self.assertEqual(pack.lot_id, self.lot11)
                lot11_found = True
            else:
                self.assertEqual(pack.lot_id, self.lot12)
                lot12_found = True
        self.assertTrue(lot11_found)
        self.assertTrue(lot12_found)

        # check quantities
        lot10_qty = self._stock_quantity(
            self.product_14, self.lot10, self.stock_location)
        self.assertEqual(lot10_qty[self.product_14.id]['qty_available'], 0)
        lot11_qty = self._stock_quantity(
            self.product_13, self.lot11, self.stock_location)
        self.assertEqual(lot11_qty[self.product_13.id]['qty_available'], 1)
        lot12_qty = self._stock_quantity(
            self.product_12, self.lot12, self.stock_location)
        self.assertEqual(lot12_qty[self.product_12.id]['qty_available'], 0)

        # I'll try to confirm it to check lot reservation:
        # lot11 has 1 availability and order4 has quantity 2
        with self.assertRaises(Warning):
            self.order4.action_button_confirm()

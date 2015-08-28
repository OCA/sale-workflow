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
        self.supplier_location = self.env['ir.model.data'].xmlid_to_res_id(
            'stock.stock_location_suppliers')
        self.stock_location = self.env['ir.model.data'].xmlid_to_res_id(
            'stock.stock_location_stock')

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

        self.order = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.sol1 = self.env['sale.order.line'].create({
            'name': 'sol1',
            'order_id': self.order.id,
            'lot_id': self.lot10.id,
            'product_id': self.product_14.id,
        })
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
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location})
        self.env['stock.move'].create({
            'name': self.product_12.name,
            'product_id': self.product_12.id,
            'product_uom_qty': 1,
            'product_uom': self.product_12.uom_id.id,
            'picking_id': picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location})
        self.env['stock.move'].create({
            'name': self.product_13.name,
            'product_id': self.product_13.id,
            'product_uom_qty': 1,
            'product_uom': self.product_13.uom_id.id,
            'picking_id': picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location})
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
            'default_picking_type_id': picking_in.id}).create({})
        for item in pick_wizard.item_ids:
            if item.product_id == self.product_14:
                item.lot_id = self.lot10
            if item.product_id == self.product_13:
                item.lot_id = self.lot11
            if item.product_id == self.product_12:
                item.lot_id = self.lot12
        pick_wizard.do_detailed_transfer()
        picking_in.do_transfer()
        self.order2 = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.sol2a = self.env['sale.order.line'].create({
            'name': 'sol2a',
            'order_id': self.order2.id,
            'lot_id': self.lot11.id,
            'product_id': self.product_13.id,
        })
        self.sol2b = self.env['sale.order.line'].create({
            'name': 'sol2b',
            'order_id': self.order2.id,
            'lot_id': self.lot12.id,
            'product_id': self.product_12.id,
        })
        self.order.action_button_confirm()
        picking = self.order.picking_ids
        picking.action_assign()
        picking.do_enter_transfer_details()
        wiz = self.env['stock.transfer_details'].search([
            ['picking_id', '=', picking.id]])
        wiz.do_detailed_transfer()
        for pack in picking.pack_operation_ids:
            if pack.product_id.id == self.product_14.id:
                self.assertEqual(pack.lot_id, self.lot10)
        # I'll try to create a sale order with lot10
        # and confirm it to check lot reservation
        self.order_test = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.order_line_test_1 = self.env['sale.order.line'].create({
            'name': 'sol_test_1',
            'order_id': self.order_test.id,
            'lot_id': self.lot10.id,
            'product_id': self.product_14.id,
        })

        # also test on_change for order_test
        onchange_res = self.registry(
            'sale.order.line'
        ).product_id_change_with_wh(
            self.cr, self.uid, [], self.order_test.pricelist_id.id,
            self.order_line_test_1.product_id.id,
            qty=self.order_line_test_1.product_uom_qty,
            uom=self.order_line_test_1.product_uom.id, qty_uos=0, uos=False,
            name='', partner_id=self.order_test.partner_id.id,
            lang=False, update_tax=True, date_order=self.order_test.date_order,
            packaging=False, fiscal_position=False, flag=False,
            warehouse_id=self.order_test.warehouse_id.id,
            context=self.env.context)
        self.assertEqual(onchange_res['domain']['lot_id'], [('id', 'in', [])])

        with self.assertRaises(Warning):
            self.order_test.action_button_confirm()

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
        for pack in picking.pack_operation_ids:
            if pack.product_id.id == self.product_13.id:
                self.assertEqual(pack.lot_id, self.lot11)
            else:
                self.assertEqual(pack.lot_id, self.lot12)

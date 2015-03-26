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

from openerp.tests import common


class TestAmendment(common.TransactionCase):

    def setUp(self):
        super(TestAmendment, self).setUp()
        self.amendment_model = self.env['sale.order.amendment']
        self.sale_model = self.env['sale.order']
        self.sale_line_model = self.env['sale.order.line']
        self.partner1 = self.env.ref('base.res_partner_2')
        self.product1 = self.env.ref('product.product_product_7')
        self.product2 = self.env.ref('product.product_product_9')

    def _create_sale(self, line_products):
        """ Create a sales order.

        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            lines.append(
                (0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': qty,
                    'product_uom': product.uom_id.id,
                    'price_unit': 50,
                })
            )
        return self.sale_model.create({
            'partner_id': self.partner1.id,
            'order_line': lines,
        })

    def _split_picking(self, picking, moves):
        """ Split a picking

        ``moves`` is a list of tuples [(move, quantity to split)]
        """
        transfer_model = self.env['stock.transfer_details'].with_context(
            active_model='stock.picking',
            active_id=picking.id,
            active_ids=picking.ids
        )
        items = []
        for move, quantity in moves:
            items.append((0, 0, {
                'quantity': quantity,
                'product_id': move.product_id.id,
                'product_uom_id': move.product_id.uom_id.id,
                'sourceloc_id': move.location_id.id,
                'destinationloc_id': move.location_dest_id.id,
            }))
        transfer = transfer_model.create({
            'picking_id': picking.id,
            'item_ids': items
        })
        transfer.with_context(do_only_split=True).do_detailed_transfer()

    def test_amendment(self):
        sale = self._create_sale([(self.product1, 1000)])

        # generate the picking
        sale.action_button_confirm()
        self.assertEqual(len(sale.picking_ids), 1)

        # ship 200 products
        picking = sale.picking_ids
        picking.force_assign()
        picking.do_prepare_partial()
        picking.pack_operation_ids[0].product_qty = 200
        picking.do_transfer()
        self.assertEqual(picking.state, 'done')
        self.assertEqual(len(sale.picking_ids), 2)

        # split the 800 remaining in 300 and 500
        picking = sale.picking_ids.filtered(lambda p: p.state != 'done')
        self._split_picking(picking, [(picking.move_lines[0], 300)])
        self.assertEqual(len(sale.picking_ids), 3)

        # cancel the picking with 300
        picking = sale.picking_ids.filtered(
            lambda p: p.move_lines[0].product_qty == 300
        )
        picking.action_cancel()
        self.assertEqual(picking.state, 'cancel')

        # 500 remains
        picking = sale.picking_ids.filtered(lambda p: p.state == 'confirmed')
        self.assertEqual(picking.move_lines[0].product_qty, 500)

        # the sale order is in shipping exception
        self.assertEqual(sale.state, 'shipping_except')

        # amend the sale order
        amendment = self.amendment_model.with_context(
            active_model='sale.order',
            active_id=sale.id,
            active_ids=sale.ids,
        ).create({'sale_id': sale.id})

        self.assertEqual(len(amendment.item_ids), 1)
        item = amendment.item_ids
        self.assertEqual(item.ordered_qty, 1000)
        self.assertEqual(item.shipped_qty, 200)
        self.assertEqual(item.canceled_qty, 300)
        self.assertEqual(item.amend_qty, 500)

    def test_amendment_cancel_one_line(self):
        sale = self._create_sale([(self.product1, 1000),
                                  (self.product2, 500)])

        # generate the picking
        sale.action_button_confirm()
        self.assertEqual(len(sale.picking_ids), 1)

        # split; put the product2 in another picking
        picking = sale.picking_ids
        move = picking.move_lines.filtered(
            lambda m: m.product_id == self.product2
        )
        self._split_picking(picking, [(move, 500)])
        self.assertEqual(len(sale.picking_ids), 2)

        # cancel the picking with the product2
        picking = sale.picking_ids.filtered(
            lambda p: p.move_lines[0].product_id == self.product2
        )
        picking.action_cancel()
        self.assertEqual(picking.state, 'cancel')

        # the sale order is in shipping exception
        self.assertEqual(sale.state, 'shipping_except')

        # amend the sale order
        amendment = self.amendment_model.with_context(
            active_model='sale.order',
            active_id=sale.id,
            active_ids=sale.ids,
        ).create({'sale_id': sale.id})

        self.assertEqual(len(amendment.item_ids), 2)
        for item in amendment.item_ids:
            if item.sale_line_id.product_id == self.product1:
                self.assertEqual(item.ordered_qty, 1000)
                self.assertEqual(item.shipped_qty, 0)
                self.assertEqual(item.canceled_qty, 0)
                self.assertEqual(item.amend_qty, 1000)
            elif item.sale_line_id.product_id == self.product2:
                self.assertEqual(item.ordered_qty, 500)
                self.assertEqual(item.shipped_qty, 0)
                self.assertEqual(item.canceled_qty, 500)
                self.assertEqual(item.amend_qty, 0)
            else:
                self.fail('Wrong product')

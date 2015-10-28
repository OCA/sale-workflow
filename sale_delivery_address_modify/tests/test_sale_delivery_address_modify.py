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


class TestSaleDeliveryAddressModify(TransactionCase):

    def test_01_modify_delivery_address(self):
        """ Deliver a backorder to the modified delivery address on the sales \
        order """
        partner = self.env['res.partner'].search(
            [('customer', '=', True), ('is_company', '=', True)], limit=1)
        shipping_partner1 = self.env['res.partner'].create({
            'name': 'Shipping address 1',
            'parent_id': partner.id,
            'use_parent_address': True,
            'type': 'delivery',
        })
        shipping_partner2 = shipping_partner1.copy(
            {'name': 'Shipping address 2'})

        # Create a sales order with two lines
        sale_vals = {
            'partner_id': partner.id,
            'order_policy': 'manual',
        }
        sale_vals.update(self.env['sale.order'].onchange_partner_id(
            partner.id)['value'])
        sale_vals['partner_shipping_id'] = shipping_partner1.id
        sale_order = self.env['sale.order'].create(sale_vals)
        for product in self.env['product.product'].search(
                [('sale_ok', '=', True)], limit=2):
            line_vals = {
                'product_id': product.id,
                'order_id': sale_order.id}
            line_vals.update(
                self.env['sale.order.line'].product_id_change(
                    sale_order.pricelist_id.id,
                    product.id, partner_id=sale_order.partner_id.id,
                    date_order=sale_order.date_order)['value'])
            self.env['sale.order.line'].create(line_vals)
        sale_order.signal_workflow('order_confirm')

        # Deliver the sales order picking partially and check backorder
        picking = sale_order.picking_ids[0]
        picking.force_assign()
        transfer = self.env['stock.transfer_details'].with_context(
            active_ids=picking.ids,
            active_model='stock.picking').create(
            {'picking_id': picking.id})
        self.assertEqual(len(transfer.item_ids), 2)
        transfer.item_ids[0].unlink()
        transfer.do_detailed_transfer()
        self.assertEqual(len(sale_order.picking_ids), 2)
        picking2 = sale_order.picking_ids - picking

        # Check that a modified address on the sales order is propagated
        # to the backorder only.
        sale_order.write(
            {'partner_shipping_id': shipping_partner2.id})
        self.assertEqual(picking.partner_id, shipping_partner1)
        self.assertEqual(picking2.partner_id, shipping_partner2)

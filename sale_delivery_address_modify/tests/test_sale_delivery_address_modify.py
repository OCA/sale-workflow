# -*- coding: utf-8 -*-
# © 2015 Stefan Rijnhart - Opener B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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

        # Using old API as per https://github.com/odoo/odoo/pull/11563
        shipping_partner2 = self.env['res.partner'].browse(
            self.registry('res.partner').copy(
                self.env.cr, self.env.uid, shipping_partner1.id,
                {'name': 'Shipping address 2'}))

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

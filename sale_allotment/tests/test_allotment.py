# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestAllotment(TransactionCase):
    def test_picking_allotment(self):
        """SO lines with allotments are dispatched to different pickings"""
        partner_id = self.ref('base.res_partner_2')
        sale = self.env['sale.order'].create(
            {'partner_id': partner_id})
        for i in range(5):
            contact = self.env['res.partner'].create(
                {'name': 'contact %d' % i,
                 'parent_id': partner_id})
            self.env['sale.order.line'].create(
                {'order_id': sale.id,
                 'product_id': self.ref('product.product_product_7'),
                 'product_uom_qty': 22.0,
                 'address_allotment_id': contact.id})
        self.assertEqual(len(sale.order_line), 5)
        sale.action_ship_create()
        self.assertEqual(len(sale.picking_ids), 5)
        self.assertItemsEqual(
            sale.order_line.mapped("address_allotment_id"),
            sale.picking_ids.mapped("partner_id"),
            "The partners of deliveries must be the alloted ones")

    def test_picking_no_allotment(self):
        """SO lines without allotments are dispatched to same pickings"""
        sale = self.env['sale.order'].create(
            {'partner_id': self.ref('base.res_partner_2')})
        for _i in range(5):
            self.env['sale.order.line'].create(
                {'order_id': sale.id,
                 'product_id': self.ref('product.product_product_7'),
                 'product_uom_qty': 22.0})
        self.assertEqual(len(sale.order_line), 5)
        sale.action_ship_create()
        self.assertEqual(len(sale.picking_ids), 1)
        self.assertEqual(sale.partner_id, sale.picking_ids.partner_id)

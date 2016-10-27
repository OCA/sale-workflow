# -*- coding: utf-8 -*-
# Copyright (C) 2016  KMEE - Hendrix Costa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.sale.tests.test_sale_common import TestSale


class TestInvoiceSaleLink(TestSale):
    def test_00_invoice_sale_link(self):
        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': p.name, 'product_id': p.id, 'product_uom_qty': 2,
                'product_uom': p.uom_id.id, 'price_unit': p.list_price
            }) for (_, p) in self.products.iteritems()],
        })
        self.so.action_confirm()
        self.so.action_invoice_create()
        self.assertEqual(len(self.so.invoice_ids), 1)
        self.assertEqual(self.so.ids, self.so.invoice_ids[0].sale_ids.ids)

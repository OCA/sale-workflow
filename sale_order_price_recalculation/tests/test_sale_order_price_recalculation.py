# -*- coding: utf-8 -*-
# Copyright 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestSaleOrderPriceRecalculation(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderPriceRecalculation, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line_model = self.env['sale.order.line']
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
        })
        self.product = self.env.ref('product.product_product_4')
        self.product = self.env['product.product'].create({
            'name': 'Jacket - Color: Black - Size: XL',
        })
        self.sale_order = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.env.ref('product.list0').id,
        })
        self.product.uos_id = self.env.ref('product.product_uom_kgm')
        line_vals = {
            'product_id': self.product.id,
            'name': self.product.name,
            'product_uom_qty': 1.0,
            'product_uom': self.product.uom_id.id,
            'price_unit': self.product.lst_price,
            'order_id': self.sale_order.id,
        }
        self.sale_order_line = self.sale_order_line_model.create(line_vals)

    def test_price_recalculation(self):
        # Check current price
        self.sale_order_line.name = u"My product description"
        self.assertEqual(
            self.sale_order_line.price_unit, self.product.lst_price)
        # Change price
        self.product.lst_price = 500
        # Launch recalculation
        self.sale_order.recalculate_prices()
        # Check if the price has been updated
        self.assertEqual(
            self.sale_order_line.price_unit, self.product.lst_price)
        # Check if quantities have changed
        self.assertEqual(self.sale_order_line.product_uom_qty, 1.0)
        # Check the description still unchanged
        self.assertEqual(self.sale_order_line.name, u"My product description")

    def test_name_recalculation(self):
        self.sale_order_line.price_unit = 150.0
        initial_price = self.sale_order_line.price_unit
        self.assertEqual(
            self.sale_order_line.name, self.product.name
        )
        self.sale_order_line.name = 'Custom Jacket'
        self.sale_order.recalculate_names()
        self.assertEquals(u"Jacket - Color: Black - Size: XL",
                          self.sale_order_line.name)
        # Check the price wasn't reset
        self.assertEquals(initial_price,
                          self.sale_order_line.price_unit)

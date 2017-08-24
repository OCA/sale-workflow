# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSale(TransactionCase):

    def setUp(self):
        super(TestSale, self).setUp()

        self.tax = self.env["account.tax"].create({
            'name': 'Unittest tax',
            'amount_type': 'percent',
            'amount': '0',
        })

        price_category_1 = self.env['product.price.category'].create({
            'name': 'TEST_CAT'
        })
        price_category_2 = self.env['product.price.category'].create({
            'name': 'TEST_CAT_2'
        })

        self.pricelist = self.env['product.pricelist'].create({
            'name': 'Unittest Pricelist',
            'item_ids': [
                (0, False, {
                    'applied_on': '2b_product_price_category',
                    'price_category_id': price_category_2.id,
                    'compute_price': 'percentage',
                    'percent_price': 5,
                })
            ],
        })

        # P1 with price_category_1
        self.p1 = self.env['product.product'].create({
            'name': 'Unittest P1',
            'price_category_id': price_category_1.id,
            'list_price': 10,
            'taxes_id': [(6, False, [self.tax.id])],
        })

        # P2 with price_category_2
        self.p2 = self.env['product.product'].create({
            'name': 'Unittest P2',
            'price_category_id': price_category_2.id,
            'list_price': 20,
            'taxes_id': [(6, False, [self.tax.id])],
        })

        # P3 without price category
        self.p3 = self.env['product.product'].create({
            'name': 'Unittest P3',
            'list_price': 30,
            'taxes_id': [(6, False, [self.tax.id])],
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Unittest partner',
        })

        self.sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, False, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom_qty': 1,
                    'product_uom': self.ref('product.product_uom_unit'),
                }),
                (0, False, {
                    'name': self.p1.name,
                    'product_id': self.p2.id,
                    'product_uom_qty': 1,
                    'product_uom': self.ref('product.product_uom_unit'),
                }),
                (0, False, {
                    'name': self.p1.name,
                    'product_id': self.p3.id,
                    'product_uom_qty': 1,
                    'product_uom': self.ref('product.product_uom_unit'),
                }),
            ]
        })

    def test_sale_without_pricelist(self):
        for line in self.sale.order_line:
            line.product_id_change()

        self.assertEqual(10, self.sale.order_line[0].price_total)
        self.assertEqual(20, self.sale.order_line[1].price_total)
        self.assertEqual(30, self.sale.order_line[2].price_total)

        self.assertEqual(60, self.sale.amount_total)

    def test_sale_with_pricelist(self):
        self.sale.pricelist_id = self.pricelist
        for line in self.sale.order_line:
            line.product_id_change()

        # Pricelist should be applied only on product with price_category_2
        self.assertEqual(10, self.sale.order_line[0].price_total)
        self.assertEqual(19, self.sale.order_line[1].price_total)
        self.assertEqual(30, self.sale.order_line[2].price_total)

        self.assertEqual(59, self.sale.amount_total)

    def test_sale_with_pricelist_and_tax(self):
        self.tax.amount = 20

        self.sale.pricelist_id = self.pricelist
        for line in self.sale.order_line:
            line.product_id_change()

        self.assertEqual(12, self.sale.order_line[0].price_total)
        self.assertEqual(22.8, self.sale.order_line[1].price_total)
        self.assertEqual(36, self.sale.order_line[2].price_total)

        self.assertEqual(70.8, self.sale.amount_total)

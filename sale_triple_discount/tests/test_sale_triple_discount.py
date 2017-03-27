# -*- coding: utf-8 -*-
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleTripleDiscount(TransactionCase):

    def create_sale_order(self):
        self.so_model = self.env['sale.order']
        self.so_line_model = self.env['sale.order.line']
        self.so = self.so_model.create({
            'partner_id': self.customer.id})
        self.so_line = self.so_line_model.create({
            'name': '/',
            'order_id': self.so.id,
            'product_id': self.product.id})
        self.so_line.onchange_product_id()

    def setUp(self):
        super(TestSaleTripleDiscount, self).setUp()
        self.inv_model = self.env['account.invoice']
        self.inv_line_model = self.env['account.invoice.line']
        self.customer = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_3')
        self.product.invoice_policy = 'order'
        self.customer.default_discount1 = 20.0
        self.customer.default_discount2 = 10.0
        self.customer.default_discount3 = 5.0
        self.create_sale_order()

    def test_so_line_onchange_product_id(self):
        self.assertEqual(
            self.so_line.discount1, self.customer.default_discount1)
        self.assertEqual(
            self.so_line.discount2, self.customer.default_discount2)
        self.assertEqual(
            self.so_line.discount3, self.customer.default_discount3)
        self.assertEqual(self.so_line.discount, 31.6)

    def test_inv_line_onchange_product_id(self):
        account_type_expenses = self.env.ref(
            'account.data_account_type_expenses')
        account = self.env['account.account'].search(
            [('user_type_id', '=', account_type_expenses.id)], limit=1)
        inv = self.env['account.invoice'].create({
            'partner_id': self.customer.id})
        inv_line = self.inv_line_model.create({
            'name': '/',
            'invoice_id': inv.id,
            'account_id': account.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'price_unit': 100.0})
        inv_line.onchange_product_id()
        self.assertEqual(
            inv_line.discount1, self.customer.default_discount1)
        self.assertEqual(
            inv_line.discount2, self.customer.default_discount2)
        self.assertEqual(
            inv_line.discount3, self.customer.default_discount3)
        self.assertEqual(inv_line.discount, 31.6)

    def test_prepare_invoice_line(self):
        self.so.action_confirm()
        inv_id = self.so.action_invoice_create()
        self.assertEqual(
            self.so.invoice_status,
            'invoiced',
            'SO invoice_status should be "invoiced" instead of "%s" '
            'after invoicing' % self.so.invoice_status)
        self.assertEqual(len(inv_id), 1)
        inv = self.env['account.invoice'].browse(inv_id)
        self.assertEqual(len(inv.invoice_line_ids), 1)
        inv_line = inv.invoice_line_ids[0]
        self.assertEqual(
            inv_line.discount1, self.so_line.discount1)
        self.assertEqual(
            inv_line.discount2, self.so_line.discount2)
        self.assertEqual(
            inv_line.discount3, self.so_line.discount3)
        self.assertEqual(inv_line.discount, 31.6)

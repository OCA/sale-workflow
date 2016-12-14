# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestSaleWaitForPayment(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestSaleWaitForPayment, self).setUp()
        self.product_obj = self.env['product.product']
        self.customer_obj = self.env['res.partner']
        self.sale_obj = self.env['sale.order']
        self.sale_line_obj = self.env['sale.order.line']

    def test_no_procurement_control(self):
        # lets set both the settings to False
        self.env["sale.config.settings"].create({
            'default_procurement_product': 0,
            'default_procurement_customer': 0,
        }).execute()

        # Case 1 : product and customer are not blacklisted
        self.createProduct(False)
        self.createCustomer(False)
        self.createSO()
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids)

        # Case 2 : product and customer are  blacklisted
        self.createProduct(True)
        self.createCustomer(True)
        self.createSO()
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids)

    def test_product_procurement_control(self):
        # Lets set appropriate settings
        self.env["sale.config.settings"].create({
            'default_procurement_product': 1,
            'default_procurement_customer': 0,
        }).execute()

        # Case 1 : product and customer are not blacklisted
        self.createProduct(False)
        self.createCustomer(False)
        self.createSO()
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids)

        # Case 2 : product is not blacklisted and customer is blacklisted
        self.createProduct(False)
        self.createCustomer(True)
        self.createSO()
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids)

        # Case 3 : product and customer are  blacklisted
        self.createProduct(True)
        self.createCustomer(True)
        self.createSO()
        self.so.action_confirm()
        self.assertFalse(self.so.picking_ids)

        # Case 4 : product is blacklisted , customer is not  blacklisted
        self.createProduct(True)
        self.createCustomer(False)
        self.createSO()
        self.so.action_confirm()
        self.assertFalse(self.so.picking_ids)

    def test_customer_procurement_control(self):
        # Lets set appropriate settings
        self.env["sale.config.settings"].create({
            'default_procurement_product': 0,
            'default_procurement_customer': 1,
        }).execute()

        # Case 1 : product and customer are not blacklisted
        self.createProduct(False)
        self.createCustomer(False)
        self.createSO()
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids)

        # Case 2 : product is not blacklisted and customer is blacklisted
        self.createProduct(False)
        self.createCustomer(True)
        self.createSO()
        self.so.action_confirm()
        self.assertFalse(self.so.picking_ids)

        # Case 3 : product and customer are  blacklisted
        self.createProduct(True)
        self.createCustomer(True)
        self.createSO()
        self.so.action_confirm()
        self.assertFalse(self.so.picking_ids)

        # Case 4 : product is blacklisted , customer is not  blacklisted
        self.createProduct(True)
        self.createCustomer(False)
        self.createSO()
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids)

    def test_both_procurement_control(self):
        # lets set appropriate settings
        self.env["sale.config.settings"].create({
            'default_procurement_product': 1,
            'default_procurement_customer': 1,
        }).execute()

        # Case 1 : product and customer are not blacklisted
        self.createProduct(False)
        self.createCustomer(False)
        self.createSO()
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids)

        # Case 2 : product is not blacklisted and customer is blacklisted
        self.createProduct(False)
        self.createCustomer(True)
        self.createSO()
        self.so.action_confirm()
        self.assertFalse(self.so.picking_ids)

        # Case 3 : product and customer are  blacklisted
        self.createProduct(True)
        self.createCustomer(True)
        self.createSO()
        self.so.action_confirm()
        self.assertFalse(self.so.picking_ids)

        # Case 4 : product is blacklisted , customer is not  blacklisted
        self.createProduct(True)
        self.createCustomer(False)
        self.createSO()
        self.so.action_confirm()
        self.assertFalse(self.so.picking_ids)

    def createSO(self):
        orderline_values = {
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
            'name': self.product.name,
        }

        values = {
            'partner_id': self.customer.id,
            'partner_invoice_id': self.customer.id,
            'partner_shipping_id': self.customer.id,
            'order_line': [(0, 0, orderline_values)]
        }
        self.so = self.sale_obj.create(values)

    def createProduct(self, blacklist):
        values = {
            'name': 'Test Product',
            'type': 'product',
            'invoice_policy': 'order',
            'lst_price': 1.0,
            'x_whitelist_blacklist': blacklist,
        }
        self.product = self.product_obj.create(values)

    def createCustomer(self, blacklist):
        values = {
            'name': 'Test Customer',
            'customer': True,
            'x_whitelist_blacklist': blacklist,
        }
        self.customer = self.customer_obj.create(values)

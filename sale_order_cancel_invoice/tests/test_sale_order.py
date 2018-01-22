# -*- coding: utf-8 -*-
# Copyright 2018 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests


class TestSaleOrderCancelInvoice(odoo.tests.TransactionCase):

    def setUp(self):
        super(TestSaleOrderCancelInvoice, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line_model = self.env['sale.order.line']

        # Data
        self.product = self.env['product.product'].create({
            'name': 'test product',
        })
        self.customer = self.env['res.partner'].create({
            'name': 'test Customer',
            'customer': True,
        })

    def _create_invoice_from_sale(self, sale):
        payment = self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': 'all'
        })
        sale_context = {
            'active_id': sale.id,
            'active_ids': sale.ids,
            'active_model': 'sale.order',
            'open_invoices': True,
        }
        res = payment.with_context(sale_context).create_invoices()
        invoice_id = res['res_id']
        return invoice_id

    @odoo.tests.common.at_install(True)
    @odoo.tests.common.post_install(True)
    def test_sales_order(self):

        sale_order = self.sale_order_model.create({
            'partner_id': self.customer.id,
        })
        sale_order_line = self.sale_order_line_model.create({
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'order_id': sale_order.id
        })

        # confirm quotation
        sale_order.action_confirm()

        self.assertEquals(sale_order.invoice_status, 'to invoice',
                          "The invoice status should be To Invoice")

        self._create_invoice_from_sale(sale_order)
        self.assertEquals(sale_order.invoice_status, 'invoiced',
                          "The invoice status should be Invoiced")

        sale_order.action_cancel()
        self.assertEquals(sale_order.invoice_ids.state, 'cancel',
                          "The invoice status should be 'cancel'")

        sale_order.action_confirm()
        self.assertEquals(sale_order.invoice_status, 'to invoice',
                          "The invoice status should be To Invoice")
        self._create_invoice_from_sale(sale_order)
        self.assertEquals(sale_order.invoice_status, 'invoiced',
                          "The invoice status should be Invoiced")

        values = {
            'order_line': [(1, sale_order_line.id, {'product_uom_qty': 2})],
        }
        sale_order.write(values)
        self.assertEquals(sale_order.invoice_ids[-1].state, 'cancel',
                          "The invoice status should be 'cancel'")
        self.assertEquals(sale_order.invoice_status, 'to invoice',
                          "The invoice status should be To Invoice")
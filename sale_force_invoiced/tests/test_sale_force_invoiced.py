# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleForceInvoiced(TransactionCase):

    def setUp(self):
        super(TestSaleForceInvoiced, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line_model = self.env['sale.order.line']

        # Data
        product_ctg = self._create_product_category()
        self.service_1 = self._create_product('test_product1',
                                              product_ctg)
        self.service_2 = self._create_product('test_product2',
                                              product_ctg)
        self.customer = self._create_customer('Test Customer')

    def _create_customer(self, name):
        """Create a Partner."""
        return self.env['res.partner'].create({
            'name': name,
            'email': 'example@yourcompany.com',
            'customer': True,
            'phone': 123456,
        })

    def _create_product_category(self):
        product_ctg = self.env['product.category'].create({
            'name': 'test_product_ctg',
        })
        return product_ctg

    def _create_product(self, name, product_ctg):
        product = self.env['product.product'].create({
            'name': name,
            'categ_id': product_ctg.id,
            'type': 'service',
            'invoice_policy': 'order',
        })
        return product

    def _create_invoice_from_sale(self, sale):
        payment = self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': 'delivered'
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

    def test_sales_order(self):
        so = self.sale_order_model.create({
            'partner_id': self.customer.id,
        })
        sol1 = self.sale_order_line_model.create({
            'product_id': self.service_1.id,
            'product_uom_qty': 1,
            'order_id': so.id
        })
        sol2 = self.sale_order_line_model.create({
            'product_id': self.service_2.id,
            'product_uom_qty': 2,
            'order_id': so.id
        })

        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 1
        sol2.qty_delivered = 2

        self.assertEquals(so.invoice_status, 'to invoice',
                          "The invoice status should be To Invoice")

        self._create_invoice_from_sale(so)
        self.assertEquals(so.invoice_status, 'invoiced',
                          "The invoice status should be Invoiced")

        # Reduce the invoiced qty
        for line in sol2.invoice_lines:
            line.quantity = 1

        self.assertEquals(so.invoice_status, 'to invoice',
                          "The invoice status should be To Invoice")

        so.action_done()
        so.force_invoiced = True
        self.assertEquals(so.invoice_status, 'invoiced',
                          "The invoice status should be Invoiced")

        so.force_invoiced = False
        self.assertEquals(so.invoice_status, 'to invoice',
                          "The invoice status should be To Invoice")

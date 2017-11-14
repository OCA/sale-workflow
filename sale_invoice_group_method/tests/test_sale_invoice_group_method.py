# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestSaleInvoiceGroupMethod(TransactionCase):

    def setUp(self):
        super(TestSaleInvoiceGroupMethod, self).setUp()
        self.users_obj = self.env['res.users']
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line_model = self.env['sale.order.line']
        self.account_payment_term = self.env['account.payment.term']
        self.sale_invoice_group_method = self.env['sale.invoice.group.method']

        # company
        self.company1 = self.env.ref('base.main_company')

        # customer
        self.customer = self._create_customer('Test Customer')

        # product
        product_ctg = self._create_product_category()
        self.service_1 = self._create_product('test_product1',
                                              product_ctg)
        self.service_2 = self._create_product('test_product2',
                                              product_ctg)

        # payment term
        self.payment_term_1 = self._create_payment_term('test1', self.company1)
        self.payment_term_2 = self._create_payment_term('test2', self.company1)

        # sale invoice group method
        field_id = self.env['ir.model.fields'].search(
            [('name', '=', 'payment_term_id'),
             ('model_id', '=', 'sale.order')],
            limit=1).id
        self.sale_invoice_group_method = \
            self._create_sale_invoice_group_method('test', field_id)

    def _create_customer(self, name):
        """Create a Partner."""
        return self.env['res.partner'].create({
            'name': name,
            'email': 'example@yourcompany.com',
            'customer': True,
            'phone': 123456,
            'currency_id': self.env.ref('base.EUR'),
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
        })
        return product

    def _create_payment_term(self, name, company):
        payment_term = self.account_payment_term.create({
            'name': name,
            'company_id': company.id,
        })
        return payment_term

    def _create_sale_invoice_group_method(self, name, field):
        invoice_group_method = self.sale_invoice_group_method.create({
            'name': name,
            'criteria_fields_ids': [(4, field)],
        })
        return invoice_group_method

    def values_sale_order(self):
        return {
            'partner_id': self.customer.id,
        }

    def _create_sale_order(self, payment_term=False, group_method=False):
        so = self.sale_order_model.create({
            'partner_id': self.customer.id,
            'payment_term_id': payment_term.id,

        })
        sol1 = self.sale_order_line_model.create({
            'product_id': self.service_1.id,
            'product_uom_qty': 1,
            'order_id': so.id,
        })
        sol2 = self.sale_order_line_model.create({
            'product_id': self.service_2.id,
            'product_uom_qty': 2,
            'order_id': so.id,
        })
        # add sale invoice group method
        if group_method:
            so.invoice_group_method_id = group_method
        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 1
        sol2.qty_delivered = 2
        return so

    def _create_sale_order_lines(self, so):
        product_uom_hour = self.env.ref('product.product_uom_hour')
        sol1 = self.sale_order_line_model.create({
            'product_id': self.service_1.id,
            'product_uom': product_uom_hour.id,
            'product_uom_qty': 1,
            'order_id': so.id,
        })
        sol2 = self.sale_order_line_model.create({
            'product_id': self.service_2.id,
            'product_uom': product_uom_hour.id,
            'product_uom_qty': 2,
            'order_id': so.id,
        })
        # confirm quotation
        so.action_confirm()
        # update quantities delivered
        sol1.qty_delivered = 1
        sol2.qty_delivered = 2
        return so

    def _create_invoice_from_sale(self, sale, multi):
        data = {'advance_payment_method': 'delivered'}
        payment = self.env['sale.advance.payment.inv'].create(data)
        if multi:
            sale_context = {
                'active_ids': sale.ids,
                'active_model': 'sale.order',
                'open_invoices': True,
            }
        else:
            sale_context = {
                'active_id': sale.id,
                'active_ids': sale.ids,
                'active_model': 'sale.order',
                'open_invoices': True,
            }
        res = payment.with_context(sale_context).create_invoices()
        invoice_id = self.env['account.invoice'].browse(res['res_id'])
        return invoice_id

    def test_create_invoice_case_1(self):
        """ A user that creates two sales orders and adds to the first one the
        Invoice Group Method. """

        so1 = self._create_sale_order(self.payment_term_1,
                                      self.sale_invoice_group_method)
        so2 = self._create_sale_order(self.payment_term_1)
        inv1 = self._create_invoice_from_sale(so1, False)
        inv2 = self._create_invoice_from_sale(so2, False)
        # The result is two different invoices (one for each sale order)
        self.assertTrue(inv1 != inv2)

    def test_create_invoice_case_2(self):
        """ A user that creates two sales orders and adds to both of them the
        Invoice Group Method. """

        so1 = self._create_sale_order(self.payment_term_1,
                                      self.sale_invoice_group_method)
        so2 = self._create_sale_order(self.payment_term_1,
                                      self.sale_invoice_group_method)
        orders = self.sale_order_model.browse([so1.id, so2.id])
        invoices = self._create_invoice_from_sale(orders, True)
        # The result is one invoice with all the lines
        self.assertEquals(len(invoices), 1,
                          "There should be only one invoice.")
        self.assertEquals(len(invoices.invoice_line_ids), 4,
                          "The invoice should have 4 lines (2 from each sale "
                          "order.")

    def test_create_invoice_case_3(self):
        """ A user that creates two sales orders and adds to both of them the
        Invoice Group Method test but in the first sale order the payment
        terms will be Payment terms 1 whilst in the second sale order the
        payment terms will br Payment terms 2. """

        so1 = self._create_sale_order(self.payment_term_1,
                                      self.sale_invoice_group_method)
        so2 = self._create_sale_order(self.payment_term_2,
                                      self.sale_invoice_group_method)
        inv1 = self._create_invoice_from_sale(so1, False)
        inv2 = self._create_invoice_from_sale(so2, False)
        # The result is two different invoices (one for each sale order)
        self.assertTrue(inv1 != inv2)

    def test_create_invoice_onchange_partner_case_4(self):
        """ A company has a Default Invoice Group Method and a user creates
        two sales orders with this customer and in the second sale order
        removes the Invoice Group Method. """

        self.customer.invoice_group_method_id = self.sale_invoice_group_method
        data1 = self.values_sale_order()
        data1.update({
            'payment_term_id': self.payment_term_1.id,
        })
        so1 = self.sale_order_model.create(data1)
        so1.onchange_partner_id()
        self.assertEquals(so1.invoice_group_method_id,
                          self.sale_invoice_group_method,
                          "The invoice group method should be"
                          "'sale_invoice_group_method'")
        so1 = self._create_sale_order_lines(so1)

        data2 = self.values_sale_order()
        so2 = self.sale_order_model.create(data2)
        so2.onchange_partner_id()
        so2.invoice_group_method_id = False
        self.assertEquals(so2.invoice_group_method_id,
                          self.env['sale.invoice.group.method'],
                          "There should be no invoice group method")
        so2 = self._create_sale_order_lines(so2)
        inv1 = self._create_invoice_from_sale(so1, False)
        inv2 = self._create_invoice_from_sale(so2, False)
        # The result is two different invoices (one for each sale order)
        self.assertTrue(inv1 != inv2)

    def test_create_invoice_onchange_partner_case_5(self):
        """ A company has a Default Invoice Group Method and a user creates
        two sales orders with this customer with the same payment terms. """

        self.customer.invoice_group_method_id = self.sale_invoice_group_method
        data1 = self.values_sale_order()
        data1.update({
            'payment_term_id': self.payment_term_1.id,
        })
        so1 = self.sale_order_model.create(data1)
        so1.onchange_partner_id()
        self.assertEquals(so1.invoice_group_method_id,
                          self.sale_invoice_group_method,
                          "The invoice group method should be"
                          "'sale_invoice_group_method'")
        so1 = self._create_sale_order_lines(so1)
        data2 = self.values_sale_order()
        data2.update({
            'payment_term_id': self.payment_term_1.id,
        })
        so2 = self.sale_order_model.create(data2)
        so2.onchange_partner_id()
        self.assertEquals(so2.invoice_group_method_id,
                          self.sale_invoice_group_method,
                          "The invoice group method should be"
                          "'sale_invoice_group_method'")
        so2 = self._create_sale_order_lines(so2)
        orders = self.sale_order_model.browse([so1.id, so2.id])
        invoices = self._create_invoice_from_sale(orders, True)
        # The result is one invoice with all the lines
        self.assertEquals(len(invoices), 1,
                          "There should be only one invoice.")
        self.assertEquals(len(invoices.invoice_line_ids), 4,
                          "The invoice should have 4 lines (2 from each sale "
                          "order.")

    def test_create_invoice_onchange_partner_case_6(self):
        """ A company has a Default Invoice Group Method and a user creates
        two sales orders with this customer but in the first sale order the
        payment terms will be Payment terms 1 whilst in the second sale order
        the payment terms will br Payment terms 2. """

        self.customer.invoice_group_method_id = self.sale_invoice_group_method
        data1 = self.values_sale_order()
        data1.update({
            'payment_term_id': self.payment_term_1.id,
        })
        so1 = self.sale_order_model.create(data1)
        so1.onchange_partner_id()
        self.assertEquals(so1.invoice_group_method_id,
                          self.sale_invoice_group_method,
                          "The invoice group method should be"
                          "'sale_invoice_group_method'")
        so1 = self._create_sale_order_lines(so1)
        data2 = self.values_sale_order()
        data2.update({
            'payment_term_id': self.payment_term_1.id,
        })
        so2 = self.sale_order_model.create(data2)
        so2.onchange_partner_id()
        self.assertEquals(so2.invoice_group_method_id,
                          self.sale_invoice_group_method,
                          "The invoice group method should be"
                          "'sale_invoice_group_method'")
        so2 = self._create_sale_order_lines(so2)
        inv1 = self._create_invoice_from_sale(so1, False)
        inv2 = self._create_invoice_from_sale(so2, False)
        # The result is two different invoices (one for each sale order)
        self.assertTrue(inv1 != inv2)

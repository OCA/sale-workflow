from odoo.tests.common import TransactionCase
from datetime import datetime
from odoo.tools.float_utils import float_compare


class TestSaleOrderLine(TransactionCase):
    def setUp(self):
        super(TestSaleOrderLine, self).setUp()

        product = self.env["product.product"]
        partner = self.env["res.partner"]
        SaleOrder = self.env["sale.order"]
        SaleOrderLine = self.env["sale.order.line"]
        account_obj = self.env['account.account']
        IrModelData = self.env['ir.model.data']

        # Usefull accounts
        user_type_id = IrModelData.xmlid_to_res_id('account.data_account_type_revenue')
        self.account_rev_id = account_obj.create(
            {'code': 'X2020',
             'name': 'Sales - Test Sales Account',
             'user_type_id': user_type_id,
             'reconcile': True})
        user_type_id = IrModelData.xmlid_to_res_id(
            'account.data_account_type_receivable'
        )
        self.account_recv_id = account_obj.create(
            {'code': 'X1012',
             'name': 'Sales - Test Reicv Account',
             'user_type_id': user_type_id,
             'reconcile': True})

        # Usefull record id
        self.group_id = IrModelData.xmlid_to_res_id('account.group_account_invoice')
        self.company_id = IrModelData.xmlid_to_res_id('base.main_company')

        # Create products
        self.product_1 = product.create({
            "name": "Product 1",
            "type": 'service',
            "list_price": 150,
            "invoice_policy": "order",
            "standard_price": 100
        })
        product_template_id = self.product_1.product_tmpl_id
        product_template_id.write({'property_account_income_id': self.account_rev_id})

        self.product_2 = product.create({
            "name": "Product 2",
            "type": 'service',
            "list_price": 150,
            "invoice_policy": "order",
            "standard_price": 100
        })
        product_template_id = self.product_2.product_tmpl_id
        product_template_id.write({'property_account_income_id': self.account_rev_id})

        # Create Sales Journal
        self.journal_sale = self.env['account.journal'].create({
            'name': 'Sale Journal - Test',
            'code': 'AJ-SALE',
            'type': 'sale',
            'company_id': self.company_id,
        })

        # In order to test, I create new user and applied Invoicing & Payments group.
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test@test.com',
            'company_id': 1,
            'groups_id': [(6, 0, [self.group_id])]})

        # Create test partner
        self.partner = partner.create({
            'name': 'Test Customer',
            'email': 'testcustomer@test.com',
            'property_account_receivable_id': self.account_recv_id,
        })
        self.sale_order_1 = SaleOrder.create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'date_order': datetime.today(),
            'pricelist_id': self.env.ref('product.list0').id
        })

        # Create Order Lines
        self.sale_order_line_1 = SaleOrderLine.create({
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'product_uom_qty': 5,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': 100,
            'order_id': self.sale_order_1.id,
            'tax_id': False,
        })
        self.sale_order_line_2 = SaleOrderLine.create({
            'name': self.product_2.name,
            'product_id': self.product_2.id,
            'product_uom_qty': 4,
            'product_uom': self.product_2.uom_id.id,
            'price_unit': 200,
            'order_id': self.sale_order_1.id,
            'tax_id': False,
        })

        self.context = {"active_model": 'sale.order',
                        "active_ids": [self.sale_order_1.id],
                        "active_id": self.sale_order_1.id}

        self.assertEqual(self.sale_order_line_1.untaxed_amount_to_invoice, 0.0,
                         msg='Amount to invoice for delivered qty SO line should '
                             'zero, since its state is draft')
        self.assertEqual(self.sale_order_line_1.untaxed_amount_invoiced, 0.0,
                         msg='Amount invoiced for delivered qty SO line should zero,'
                             ' since its state is draft, and there is no'
                             ' invoice at this moment')
        self.assertEqual(self.sale_order_line_2.untaxed_amount_to_invoice, 0.0,
                         msg='Amount to invoice for ordered qty SO line should zero,'
                             ' since its state is draft')
        self.assertEqual(self.sale_order_line_2.untaxed_amount_invoiced, 0.0,
                         msg='Amount invoiced for ordered qty SO line should zero,'
                             ' since its state is draft, and there is'
                             ' no invoice at this moment')
        self.assertEqual(self.sale_order_1.untaxed_amount_to_invoice, 0.0,
                         msg='untaxed_to_amount  must be equal 0')
        self.assertEqual(self.sale_order_1.untaxed_amount_invoiced, 0.0,
                         msg='untaxed_to_amount  must be equal 0')

        self.sale_order_1.with_context(self.context).action_confirm()

    def test_untaxed_amount_invoice(self):
        """Testing to compute the untaxed amount already invoiced from the
        sale order line, taking the refund attached the so line into account."""

        self.assertEquals(self.sale_order_line_1.untaxed_amount_invoiced, 0.0,
                          msg="The amount to invoice should be zero, "
                              "as the no confirmed invoice")
        self.assertEquals(self.sale_order_line_2.untaxed_amount_invoiced, 0.0,
                          msg="The amount to invoice should be zero, "
                              "as the no confirmed invoice")
        self.assertEquals(self.sale_order_line_1.untaxed_amount_to_invoice, 500.0,
                          msg="Amount to invoice for ordered SO line "
                              "should be 500, even if there is no invoice")
        self.assertEquals(self.sale_order_line_2.untaxed_amount_to_invoice, 800.0,
                          msg="Amount to invoice for ordered SO line "
                              "should be 800, even if there is no invoice")
        self.assertEqual(self.sale_order_1.untaxed_amount_to_invoice, 1300.0,
                         msg='untaxed_to_amount  must be equal 0')
        self.assertEqual(self.sale_order_1.untaxed_amount_invoiced, 0.0,
                         msg='untaxed_to_amount  must be equal 0')

        advance_payment = self.env['sale.advance.payment.inv']

        payment = advance_payment.with_context(self.context).create({
            'advance_payment_method': 'all',
            'product_id': self.env.ref('sale.advance_product_0').id
        })

        payment.with_context(self.context).create_invoices()

        self.assertEquals(self.sale_order_1.invoice_count, 1,
                          msg='After create invoice the count'
                              ' invoices must be equal to 1')
        self.assertEqual(self.sale_order_1.untaxed_amount_to_invoice, 1300.0,
                         msg='untaxed_to_amount  must be equal 1300')
        self.assertEqual(self.sale_order_1.untaxed_amount_invoiced, 0.0,
                         msg='untaxed_to_amount  must be equal 0')

        # validate invoice
        self.sale_order_1.invoice_ids.action_invoice_open()

        self.assertEquals(self.sale_order_line_1.untaxed_amount_invoiced, 500.0,
                          msg='Amount invoiced for ordered SO line should 500,'
                              ' there is a validated invoice at this moment')
        self.assertEquals(self.sale_order_line_2.untaxed_amount_invoiced, 800.0,
                          msg='Amount invoiced for ordered SO line should 800,'
                              ' there is a validated invoice at this moment')
        self.assertEquals(self.sale_order_line_1.untaxed_amount_to_invoice, 0.0,
                          msg='Amount to invoice for ordered SO line is zero,'
                              ' since the invoice is validated')
        self.assertEquals(self.sale_order_line_2.untaxed_amount_to_invoice, 0.0,
                          msg='Amount to invoice for ordered SO line is zero,'
                              ' since the invoice is validated')
        invoice_1 = self.sale_order_1.invoice_ids[0]
        # Make a credit note
        context = {"active_model": 'account.invoice',
                   "active_ids": [invoice_1.id],
                   "active_id": invoice_1.id}
        refund = self.env['account.invoice.refund'].with_context(context).create(
            {
                'filter_refund': 'refund',
                'description': 'reason test'
            }
        )

        refund.with_context(context).invoice_refund()

        self.assertEquals(self.sale_order_line_1.untaxed_amount_invoiced, 500.0,
                          msg='Untaxed amount invoice must be equal 500 because'
                              ' we Create a draft credit note')
        self.assertEquals(self.sale_order_line_2.untaxed_amount_invoiced, 800.0,
                          msg='Untaxed amount invoice must be equal 800 because'
                              ' we Create a draft credit note')
        self.assertEquals(self.sale_order_line_1.untaxed_amount_to_invoice, 0.0,
                          msg='The amount to invoice should be zero,'
                              ' as the line based on delivered quantity')
        self.assertEquals(self.sale_order_line_2.untaxed_amount_to_invoice, 0.0,
                          msg='The amount to invoice should be zero,'
                              ' as the line based on delivered quantity')

    def test_sale_with_taxes(self):
        """ Test SO with taxes applied on its lines and check subtotal applied
         on its lines and total applied on the SO """
        # Create a tax with price included
        tax_include = self.env['account.tax'].create({
            'name': 'Tax with price include',
            'amount': 10,
            'price_include': True
        })

        # Apply taxes on the sale order lines
        self.sale_order_line_1.write({'tax_id': [(4, tax_include.id)]})
        self.sale_order_line_2.write({'tax_id': [(4, tax_include.id)]})

        # Trigger onchange to reset discount, unit price, subtotal, ...
        for line in self.sale_order_1.order_line:
            line.product_id_change()
            line._onchange_discount()

        for line in self.sale_order_1.order_line:
            if line.tax_id.price_include:
                price = line.price_unit * line.product_uom_qty - line.price_tax
            else:
                price = line.price_unit * line.product_uom_qty

            self.assertEquals(float_compare(line.price_subtotal,
                                            price,
                                            precision_digits=2), 0)

        self.assertEquals(
            self.sale_order_1.amount_total,
            self.sale_order_1.amount_untaxed + self.sale_order_1.amount_tax,
            msg='Taxes should be applied')

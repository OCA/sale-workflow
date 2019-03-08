# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.sale.tests import test_sale_common
from odoo.tests import Form
from odoo.exceptions import ValidationError, UserError


class TestSaleInvoicePlan(test_sale_common.TestCommonSaleNoChart):

    def test_01_invoice_plan(self):
        # To create all remaining invoice from SO
        ctx = {'active_id': self.so_service.id,
               'active_ids': [self.so_service.id],
               'all_remain_invoices': False}
        f = Form(self.env['sale.create.invoice.plan'])
        try:  # UserError if no installment
            plan = f.save()
        except ValidationError:
            pass
        # Create Invoice Plan 3 installment
        num_installment = 3
        f.num_installment = num_installment
        # Test 3 types of interval
        for interval_type in ['month', 'year', 'day']:
            f.interval_type = interval_type
            plan = f.save()
            # SO confirmed without invoice plan being created
            if not self.so_service.invoice_plan_ids:
                with self.assertRaises(UserError):
                    self.so_service.action_confirm()
            # Create Invocie Plan Installment
            plan.with_context(ctx).sale_create_invoice_plan()
            self.assertEquals(len(self.so_service.invoice_plan_ids),
                              num_installment,
                              'Wrong number of installment created')
        # Confirm the SO
        self.so_service.action_confirm()
        # Create one invoice
        make_wizard = self.env['sale.make.planned.invoice'].create({})
        make_wizard.with_context(ctx).create_invoices_by_plan()
        invoices = self.so_service.invoice_ids
        self.assertEquals(len(invoices), 1, 'Only 1 invoice should be crated')
        # Create all remaining invoices
        ctx['all_remain_invoices'] = True
        make_wizard.with_context(ctx).create_invoices_by_plan()
        # Valid number of invoices
        invoices = self.so_service.invoice_ids
        self.assertEquals(len(invoices), num_installment,
                          'Wrong number of invoice created')
        # Valid total quantity of invoices
        quantity = sum(invoices.mapped('invoice_line_ids').mapped('quantity'))
        self.assertEquals(quantity, 1,
                          'Wrong number of total invoice quantity')

    def test_02_invoice_plan_with_advance(self):
        # To create all remaining invoice from SO
        ctx = {'active_id': self.so_service.id,
               'active_ids': [self.so_service.id],
               'all_remain_invoices': True}
        # Create Invoice Plan 3 installment with Advance
        num_installment = 3
        f = Form(self.env['sale.create.invoice.plan'])
        f.num_installment = num_installment
        f.advance = True  # Advance
        plan = f.save()
        plan.with_context(ctx).sale_create_invoice_plan()
        self.assertEquals(len(self.so_service.invoice_plan_ids),
                          num_installment + 1,
                          'Wrong number of installment created')
        # If advance percent is not filled, show error
        with self.assertRaises(ValidationError):
            self.so_service.action_confirm()
        advance_line = self.so_service.invoice_plan_ids.\
            filtered(lambda l: l.invoice_type == 'advance')
        self.assertEquals(len(advance_line), 1, 'No one advance line')
        # Add 10% to advance
        advance_line.percent = 10
        # Can confirm the SO after advance is filled
        self.so_service.action_confirm()
        # Create all invoice plan
        wizard = self.env['sale.make.planned.invoice'].create({})
        wizard.with_context(ctx).create_invoices_by_plan()
        # Valid number of invoices, including advance
        invoices = self.so_service.invoice_ids
        self.assertEquals(len(invoices), num_installment + 1,
                          'Wrong number of invoice created')
        # Valid total quantity of invoices (exclude Advance line)
        quantity = sum(invoices.mapped('invoice_line_ids').filtered(
            lambda l: l.product_id == self.product_order).mapped('quantity'))
        self.assertEquals(quantity, 1,
                          'Wrong number of total invoice quantity')

    def test_03_unlink_invoice_plan(self):
        ctx = {'active_id': self.so_service.id,
               'active_ids': [self.so_service.id]}
        f = Form(self.env['sale.create.invoice.plan'])
        # Create Invoice Plan 3 installment
        num_installment = 3
        f.num_installment = num_installment
        plan = f.save()
        plan.with_context(ctx).sale_create_invoice_plan()
        # Remove it
        self.so_service.remove_invoice_plan()
        self.assertFalse(self.so_service.invoice_plan_ids)

    def test_04_invoice_plan_over_delivered_quantity(self):
        # To create all remaining invoice from SO
        ctx = {'active_id': self.so_product.id,
               'active_ids': [self.so_product.id],
               'all_remain_invoices': True}
        # Create Invoice Plan 2 installment
        num_installment = 2
        f = Form(self.env['sale.create.invoice.plan'])
        f.num_installment = num_installment
        plan = f.save()
        plan.with_context(ctx).sale_create_invoice_plan()
        self.so_product.action_confirm()
        # Delivery product 3 qty out of 10
        self.assertEqual(len(self.so_product.picking_ids), 1)
        pick = self.so_product.picking_ids[0]
        pick.move_ids_without_package.write({'quantity_done': 3.0})
        pick.action_done()
        # Create invoice by plan
        wizard = self.env['sale.make.planned.invoice'].create({})
        with self.assertRaises(ValidationError) as e:
            wizard.with_context(ctx).create_invoices_by_plan()
        error_message = ('Plan quantity: 5.0, exceed invoiceable quantity: 3.0'
                         '\nProduct should be delivered before invoice')
        self.assertEqual(e.exception.name, error_message)
        # Delier all the rest and create invoice plan again
        pick = self.so_product.picking_ids.filtered(lambda l:
                                                    l.state != 'done')
        pick.mapped('move_ids_without_package').write({'quantity_done': 7.0})
        pick.action_done()
        wizard = self.env['sale.make.planned.invoice'].create({})
        wizard.with_context(ctx).create_invoices_by_plan()
        # Valid total quantity of invoice = 10 units
        invoices = self.so_product.invoice_ids
        quantity = sum(invoices.mapped('invoice_line_ids').mapped('quantity'))
        self.assertEquals(quantity, 10,
                          'Wrong number of total invoice quantity')

    @classmethod
    def setUpClass(cls):
        super(TestSaleInvoicePlan, cls).setUpClass()
        cls.setUpClassicProducts()
        cls.setUpUsers()
        group_salemanager = cls.env.ref('sales_team.group_sale_manager')
        group_salesman = cls.env.ref('sales_team.group_sale_salesman')
        group_employee = cls.env.ref('base.group_user')
        cls.user_manager.write({'groups_id': [(6, 0, [group_salemanager.id,
                                                      group_employee.id])]})
        cls.user_employee.write({'groups_id': [(6, 0, [group_salesman.id,
                                                       group_employee.id])]})
        # Create an SO for Service
        cls.so_service = cls.env['sale.order'].sudo(cls.user_employee).create({
            'partner_id': cls.partner_customer_usd.id,
            'partner_invoice_id': cls.partner_customer_usd.id,
            'partner_shipping_id': cls.partner_customer_usd.id,
            'use_invoice_plan': True,
            'order_line': [
                (0, 0, {'name': cls.product_order.name,
                        'product_id': cls.product_order.id,
                        'product_uom_qty': 1,
                        'product_uom': cls.product_order.uom_id.id,
                        'price_unit': cls.product_order.list_price})
            ],
            'pricelist_id': cls.env.ref('product.list0').id,
        })
        # Create an SO for product delivery
        cls.so_product = cls.env['sale.order'].sudo(cls.user_employee).create({
            'partner_id': cls.partner_customer_usd.id,
            'partner_invoice_id': cls.partner_customer_usd.id,
            'partner_shipping_id': cls.partner_customer_usd.id,
            'use_invoice_plan': True,
            'order_line': [
                (0, 0, {'name': cls.product_deliver.name,
                        'product_id': cls.product_deliver.id,
                        'product_uom_qty': 10,
                        'product_uom': cls.product_deliver.uom_id.id,
                        'price_unit': cls.product_deliver.list_price})
            ],
            'pricelist_id': cls.env.ref('product.list0').id,
        })

# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestInvoicefinishedTask(common.SavepointCase):

    def setUp(self):
        super(TestInvoicefinishedTask, self).setUp()

        group_manager = self.env.ref('sales_team.group_sale_manager')
        self.manager = self.env['res.users'].create({
            'name': 'Andrew Manager',
            'login': 'manager',
            'email': 'a.m@example.com',
            'signature': '--\nAndreww',
            'notify_email': 'always',
            'groups_id': [(6, 0, [group_manager.id])]
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Customer - test',
            'customer': True,
        })
        self.project = self.env['project.project'].create({
            'name': "Some test project"
        })
        self.stage_new = self.env['project.task.type'].create(
            self._prepare_stage_vals())
        self.stage_invoiceable = self.env['project.task.type'].create(
            self._prepare_stage_vals(invoiceable_stage=True))
        self.uom_unit = self.env.ref('product.product_uom_unit')

        self.Product = self.env['product.product']
        self.product = self.Product.create(self._prepare_product_vals())
        product_delivery_vals = self._prepare_product_vals()
        product_delivery_vals.update({
            'name': 'Product - Service - Policy delivery - Test',
            'invoice_policy': 'delivery',
        })
        self.product_policy_delivery = self.Product.create(
            product_delivery_vals)

        self.sale_order = self.env['sale.order'].create(
            self._sale_order_vals(self.product))
        self.sale_order_policy_delivery = self.env['sale.order'].create(
            self._sale_order_vals(self.product_policy_delivery))

    def _prepare_stage_vals(self, invoiceable_stage=False):
        return {
            'name': 'Test Invoiceable',
            'sequence': 5,
            'project_ids': [(6, 0, self.project.ids)],
            'invoiceable': invoiceable_stage,
        }

    def _sale_order_vals(self, product):
        return {
            'partner_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
            'order_line': [
                (0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': 5,
                    'product_uom': product.uom_id.id,
                    'price_unit': product.list_price,
                }),
            ],
        }

    def _prepare_product_vals(self):
        return {
            'name': 'Product - Service  - Test',
            'type': 'service',
            'list_price': 100.00,
            'standard_price': 50.00,
            'invoice_policy': 'order',
            'service_tracking': 'task_global_project',
            'invoicing_finished_task': True,
            'project_id': self.project.id,
        }

    def _prepare_timesheet_vals(self, task, unit_amount):
        return {
            'name': 'Test Line',
            'project_id': self.project.id,
            'unit_amount': unit_amount,
            'product_uom_id': task.sale_line_id.product_uom.id,
            'user_id': self.manager.id,
            'task_id': task.id,
        }

    def test_invoice_status(self):
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.invoice_status, 'no')
        task = self.sale_order.order_line.task_ids

        # Add a timesheet line
        self.env['account.analytic.line'].create(
            self._prepare_timesheet_vals(task, 5.0))
        self.assertEqual(self.sale_order.invoice_status, 'no')

        # Set task in invoiceable stage
        task.stage_id = self.stage_invoiceable.id
        task._onchange_stage_id()
        self.assertEqual(self.sale_order.invoice_status, 'to invoice')

        # Click on toggle_invoiceable method
        task.toggle_invoiceable()
        self.assertEqual(self.sale_order.invoice_status, 'no')

        task.toggle_invoiceable()
        self.assertEqual(self.sale_order.invoice_status, 'to invoice')

        # Make the invoice
        self.sale_order.action_invoice_create()

        # Click on toggle_invoiceable method after the so is invoiced
        with self.assertRaises(ValidationError):
            task.toggle_invoiceable()

        self.sale_order.action_done()
        with self.assertRaises(ValidationError):
            task.write({
                'sale_line_id': self.sale_order_policy_delivery.order_line.id,
            })
        # Try to create a task and link it to so line
        with self.assertRaises(ValidationError):
            self.env['project.task'].create({
                'name': 'Other Task',
                'user_id': self.manager.id,
                'project_id': self.project.id,
                'sale_line_id': self.sale_order.order_line.id,
            })

    def test_check_qty_to_invoice(self):
        self.sale_order.action_confirm()
        task = self.sale_order.order_line.task_ids
        # Add a timesheet line
        self.env['account.analytic.line'].create(
            self._prepare_timesheet_vals(task, 10.5))
        self.assertEqual(self.sale_order.order_line.qty_to_invoice, 0.0)
        task.toggle_invoiceable()
        self.assertEqual(self.sale_order.order_line.qty_to_invoice, 5.0)
        # Set task an invoiceable state
        self.sale_order_policy_delivery.action_confirm()
        # Add a timesheet line
        task_delivery = self.sale_order_policy_delivery.order_line.task_ids
        self.env['account.analytic.line'].create(
            self._prepare_timesheet_vals(task_delivery, 10.0))
        task_delivery.write({
            'stage_id': self.stage_invoiceable.id,
        })
        task_delivery._onchange_stage_id()
        self.assertEqual(
            self.sale_order_policy_delivery.order_line.qty_to_invoice, 10.0)

    def test_create_task_stage_invoiceable(self):
        self.sale_order.action_confirm()
        task = self.env['project.task'].create({
            'name': 'Other Task',
            'user_id': self.manager.id,
            'project_id': self.project.id,
            'sale_line_id': self.sale_order.order_line.id,
        })
        task.stage_id = self.stage_invoiceable
        task._onchange_stage_id()
        self.assertTrue(task.invoiceable)

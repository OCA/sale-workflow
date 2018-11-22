# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError

from odoo.addons.sale_timesheet.tests.common import \
    TestCommonSaleTimesheetNoChart


class TestSaleTimesheetNonbillable(TestCommonSaleTimesheetNoChart):

    def setUp(self):
        super().setUp()

        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.ProjectTask = self.env['project.task']
        self.SudoProjectTask = self.ProjectTask.sudo()
        self.SaleOrder = self.env['sale.order']
        self.SudoSaleOrder = self.SaleOrder.sudo()
        self.SaleOrderLine = self.env['sale.order.line']
        self.SudoSaleOrderLine = self.SaleOrderLine.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.AccountAccount = self.env['account.account']
        self.SudoAccountAccount = self.AccountAccount.sudo()
        self.ProductProduct = self.env['product.product']
        self.SudoProductProduct = self.ProductProduct.sudo()
        self.uom_hours = self.env.ref('uom.product_uom_hour')

    def test_1(self):
        account = self.SudoAccountAccount.create({
            'code': 'TEST-1',
            'name': 'Sales #1',
            'reconcile': True,
            'user_type_id': self.env.ref(
                'account.data_account_type_revenue'
            ).id,
        })
        project = self.SudoProject.create({
            'name': 'Project #1',
            'allow_timesheets': True,
        })
        product = self.SudoProductProduct.create({
            'name': 'Service #1',
            'standard_price': 30,
            'list_price': 90,
            'type': 'service',
            'invoice_policy': 'delivery',
            'uom_id': self.uom_hours.id,
            'uom_po_id': self.uom_hours.id,
            'default_code': 'CODE-1',
            'service_type': 'timesheet',
            'service_tracking': 'task_global_project',
            'project_id': project.id,
            'taxes_id': False,
            'property_account_income_id': account.id,
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #1',
            'timesheet_cost': 42,
        })
        sale_order = self.SudoSaleOrder.create({
            'partner_id': self.partner_customer_usd.id,
            'partner_invoice_id': self.partner_customer_usd.id,
            'partner_shipping_id': self.partner_customer_usd.id,
            'pricelist_id': self.pricelist_usd.id,
        })
        sale_order_line = self.SudoSaleOrderLine.create({
            'order_id': sale_order.id,
            'name': product.name,
            'product_id': product.id,
            'product_uom_qty': 0,
            'product_uom': self.uom_hours.id,
            'price_unit': product.list_price
        })
        sale_order.action_confirm()
        task = self.SudoProjectTask.search([
            ('sale_line_id', '=', sale_order_line.id)
        ])
        timesheet1 = self.SudoAccountAnalyticLine.create({
            'project_id': task.project_id.id,
            'task_id': task.id,
            'name': 'Entry #1-1',
            'unit_amount': 1,
            'employee_id': employee.id,
        })
        timesheet2 = self.SudoAccountAnalyticLine.create({
            'project_id': task.project_id.id,
            'task_id': task.id,
            'name': 'Entry #1-2',
            'unit_amount': 1,
            'employee_id': employee.id,
        })

        self.assertEqual(timesheet1.timesheet_invoice_type, 'billable_time')
        self.assertEqual(timesheet2.timesheet_invoice_type, 'billable_time')
        self.assertEqual(sale_order_line.qty_delivered, 2)
        self.assertEqual(sale_order_line.qty_to_invoice, 2)
        self.assertEqual(sale_order_line.qty_invoiced, 0)

        timesheet3 = self.SudoAccountAnalyticLine.create({
            'project_id': task.project_id.id,
            'task_id': task.id,
            'name': 'Entry #1-3',
            'unit_amount': 1,
            'employee_id': employee.id,
        })
        self.assertEqual(timesheet3.timesheet_invoice_type, 'billable_time')
        self.assertEqual(sale_order_line.qty_delivered, 3)
        self.assertEqual(sale_order_line.qty_to_invoice, 3)
        self.assertEqual(sale_order_line.qty_invoiced, 0)

        timesheet2.write({
            'timesheet_exclude_from_billing': True,
        })
        timesheet2._onchange_task_id_employee_id()
        self.assertEqual(timesheet1.timesheet_invoice_type, 'billable_time')
        self.assertTrue(timesheet1.so_line)
        self.assertEqual(timesheet2.timesheet_invoice_type, 'non_billable')
        self.assertFalse(timesheet2.so_line)
        self.assertEqual(timesheet3.timesheet_invoice_type, 'billable_time')
        self.assertTrue(timesheet3.so_line)

        self.assertEqual(sale_order_line.qty_delivered, 2)
        self.assertEqual(sale_order_line.qty_to_invoice, 2)
        self.assertEqual(sale_order_line.qty_invoiced, 0)

        self.assertFalse(timesheet1.timesheet_invoice_id)
        sale_order.action_invoice_create()
        self.assertTrue(timesheet1.timesheet_invoice_id)
        self.assertEqual(sale_order_line.qty_delivered, 2)
        self.assertEqual(sale_order_line.qty_to_invoice, 0)
        self.assertEqual(sale_order_line.qty_invoiced, 2)
        with self.assertRaises(UserError):
            timesheet1.write({
                'timesheet_exclude_from_billing': True,
            })

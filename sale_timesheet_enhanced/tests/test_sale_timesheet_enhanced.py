# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import UserError, ValidationError


class TestSaleTimesheetEnhanced(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.uom_hour = self.env.ref('uom.product_uom_hour')
        self.user_type_payable = self.env.ref(
            'account.data_account_type_payable'
        )
        self.user_type_receivable = self.env.ref(
            'account.data_account_type_receivable'
        )
        self.user_type_revenue = self.env.ref(
            'account.data_account_type_revenue'
        )
        self.Partner = self.env['res.partner']
        self.SudoPartner = self.Partner.sudo()
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.AccountAccount = self.env['account.account']
        self.SudoAccountAccount = self.AccountAccount.sudo()
        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.ProjectTask = self.env['project.task']
        self.SudoProjectTask = self.ProjectTask.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()
        self.ProductProduct = self.env['product.product']
        self.SudoProductProduct = self.ProductProduct.sudo()
        self.SaleOrder = self.env['sale.order']
        self.SudoSaleOrder = self.SaleOrder.sudo()
        self.SaleOrderLine = self.env['sale.order.line']
        self.SudoSaleOrderLine = self.SaleOrderLine.sudo()
        self.ProjectCreateSaleOrder = self.env['project.create.sale.order']

    def test_1(self):
        self.SudoProject._selection_proxied_billable_type()

    def test_2(self):
        project = self.SudoProject.create({
            'name': 'Project #2',
        })

        with self.assertRaises(ValidationError):
            project.manual_billable_type = 'task_rate'

    def test_3(self):
        project = self.SudoProject.create({
            'name': 'Project #3',
        })
        product = self.SudoProductProduct.create({
            'name': 'ProductProduct #3',
            'standard_price': 10,
            'list_price': 20,
            'type': 'service',
            'invoice_policy': 'delivery',
            'uom_id': self.uom_hour.id,
            'uom_po_id': self.uom_hour.id,
            'default_code': 'P3',
            'service_type': 'timesheet',
            'service_tracking': 'no',
            'project_id': False,
            'taxes_id': False,
        })
        account_payable = self.SudoAccountAccount.create({
            'code': 'AP3',
            'name': 'Payable #3',
            'user_type_id': self.user_type_payable.id,
            'reconcile': True,
        })
        account_receivable = self.SudoAccountAccount.create({
            'code': 'AR3',
            'name': 'Receivable #3',
            'user_type_id': self.user_type_receivable.id,
            'reconcile': True
        })
        partner = self.SudoPartner.create({
            'name': 'Partner #3',
            'email': 'partner3@localhost',
            'customer': True,
            'property_account_payable_id': account_payable.id,
            'property_account_receivable_id': account_receivable.id,
        })
        wizard = self.ProjectCreateSaleOrder.with_context(
            active_id=project.id,
            active_model='project.project'
        ).create({
            'product_id': product.id,
            'price_unit': 42,
            'billable_type': 'project_rate',
            'partner_id': partner.id,
        })
        self.SudoSaleOrder.browse(
            wizard.action_create_sale_order()['res_id']
        )

        self.assertEqual(project.billable_type, 'task_rate')
        self.assertEqual(project.manual_billable_type, False)
        self.assertEqual(project.proxied_billable_type, 'task_rate')

        project.manual_billable_type = 'employee_rate'
        self.assertEqual(project.billable_type, 'employee_rate')
        self.assertEqual(project.proxied_billable_type, 'employee_rate')

        project.manual_billable_type = False
        self.assertEqual(project.billable_type, 'task_rate')
        self.assertEqual(project.proxied_billable_type, 'task_rate')

        project.proxied_billable_type = 'employee_rate'
        self.assertEqual(project.billable_type, 'employee_rate')
        self.assertEqual(project.manual_billable_type, 'employee_rate')

        project.proxied_billable_type = False
        self.assertEqual(project.billable_type, 'task_rate')
        self.assertEqual(project.manual_billable_type, False)

        project.proxied_billable_type = 'employee_rate'
        project.proxied_billable_type = False
        project._onchange_proxied_billable_type()
        self.assertEqual(project.proxied_billable_type, 'task_rate')

        project.proxied_billable_type = 'task_rate'
        self.assertEqual(project.manual_billable_type, 'task_rate')
        task = self.SudoProjectTask.create({
            'name': 'ProjectTask #3',
            'project_id': project.id,
        })
        task._onchange_project()
        self.assertEqual(task.billable_type, 'task_rate')

        task.exclude_from_sale_order = True
        self.assertEqual(task.billable_type, 'no')

        task.exclude_from_sale_order = False
        self.assertEqual(task.billable_type, 'task_rate')

    def test_4(self):
        account = self.SudoAccountAccount.create({
            'code': 'TEST-4',
            'name': 'Sales #4',
            'reconcile': True,
            'user_type_id': self.user_type_revenue.id,
        })
        project = self.SudoProject.create({
            'name': 'Project #4',
            'allow_timesheets': True,
        })
        product = self.SudoProductProduct.create({
            'name': 'Service #4',
            'standard_price': 30,
            'list_price': 90,
            'type': 'service',
            'invoice_policy': 'delivery',
            'uom_id': self.uom_hour.id,
            'uom_po_id': self.uom_hour.id,
            'default_code': 'CODE-4',
            'service_type': 'timesheet',
            'service_tracking': 'task_global_project',
            'project_id': project.id,
            'taxes_id': False,
            'property_account_income_id': account.id,
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #4',
            'timesheet_cost': 42,
        })
        account_payable = self.SudoAccountAccount.create({
            'code': 'AP4',
            'name': 'Payable #4',
            'user_type_id': self.user_type_payable.id,
            'reconcile': True,
        })
        account_receivable = self.SudoAccountAccount.create({
            'code': 'AR4',
            'name': 'Receivable #4',
            'user_type_id': self.user_type_receivable.id,
            'reconcile': True
        })
        partner = self.SudoPartner.create({
            'name': 'Partner #4',
            'email': 'partner4@localhost',
            'customer': True,
            'property_account_payable_id': account_payable.id,
            'property_account_receivable_id': account_receivable.id,
        })
        sale_order = self.SudoSaleOrder.create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
        })
        sale_order_line = self.SudoSaleOrderLine.create({
            'order_id': sale_order.id,
            'name': product.name,
            'product_id': product.id,
            'product_uom_qty': 0,
            'product_uom': self.uom_hour.id,
            'price_unit': product.list_price
        })
        sale_order.action_confirm()
        task = self.SudoProjectTask.search([
            ('sale_line_id', '=', sale_order_line.id)
        ])
        timesheet1 = self.SudoAccountAnalyticLine.create({
            'project_id': task.project_id.id,
            'task_id': task.id,
            'name': 'Entry #4-1',
            'unit_amount': 1,
            'employee_id': employee.id,
        })
        timesheet2 = self.SudoAccountAnalyticLine.create({
            'project_id': task.project_id.id,
            'task_id': task.id,
            'name': 'Entry #4-2',
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
            'name': 'Entry #4-3',
            'unit_amount': 1,
            'employee_id': employee.id,
        })
        self.assertEqual(timesheet3.timesheet_invoice_type, 'billable_time')
        self.assertEqual(sale_order_line.qty_delivered, 3)
        self.assertEqual(sale_order_line.qty_to_invoice, 3)
        self.assertEqual(sale_order_line.qty_invoiced, 0)

        timesheet2.write({
            'exclude_from_sale_order': True,
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
                'exclude_from_sale_order': True,
            })

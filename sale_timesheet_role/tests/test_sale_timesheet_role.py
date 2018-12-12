# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2 import IntegrityError

from odoo.tests import common
from odoo.tools.misc import mute_logger


class TestSaleTimesheetRole(common.TransactionCase):

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
        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.Task = self.env['project.task']
        self.SudoTask = self.Task.sudo()
        self.Role = self.env['project.role']
        self.SudoRole = self.Role.sudo()
        self.Partner = self.env['res.partner']
        self.SudoPartner = self.Partner.sudo()
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()
        self.ProjectEmployeeRoleSaleOrderLineMap = self.env[
            'project.employee.role.sale.order.line.map'
        ]
        self.SudoProjectEmployeeRoleSaleOrderLineMap = (
            self.ProjectEmployeeRoleSaleOrderLineMap.sudo()
        )
        self.AccountAccount = self.env['account.account']
        self.SudoAccountAccount = self.AccountAccount.sudo()
        self.ProductProduct = self.env['product.product']
        self.SudoProductProduct = self.ProductProduct.sudo()
        self.SaleOrder = self.env['sale.order']
        self.SudoSaleOrder = self.SaleOrder.sudo()
        self.SaleOrderLine = self.env['sale.order.line']
        self.SudoSaleOrderLine = self.SaleOrderLine.sudo()
        self.ProjectCreateSaleOrder = self.env['project.create.sale.order']

    def test_1(self):
        account = self.SudoAccountAccount.create({
            'code': 'TEST-1',
            'name': 'Sales #1',
            'reconcile': True,
            'user_type_id': self.user_type_revenue.id,
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
            'uom_id': self.uom_hour.id,
            'uom_po_id': self.uom_hour.id,
            'default_code': 'CODE-1',
            'service_type': 'timesheet',
            'service_tracking': 'task_global_project',
            'project_id': project.id,
            'taxes_id': False,
            'property_account_income_id': account.id,
        })
        account_payable = self.SudoAccountAccount.create({
            'code': 'AP4',
            'name': 'Payable #1',
            'user_type_id': self.user_type_payable.id,
            'reconcile': True,
        })
        account_receivable = self.SudoAccountAccount.create({
            'code': 'AR4',
            'name': 'Receivable #1',
            'user_type_id': self.user_type_receivable.id,
            'reconcile': True
        })
        partner = self.SudoPartner.create({
            'name': 'Partner #1',
            'email': 'partner-1@localhost',
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

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            project.write({
                'sale_line_employee_role_ids': [
                    (0, 0, {
                        'sale_line_id': sale_order_line.id,
                    }),
                ],
            })

    def test_2(self):
        account = self.SudoAccountAccount.create({
            'code': 'TEST-2',
            'name': 'Sales #2',
            'reconcile': True,
            'user_type_id': self.user_type_revenue.id,
        })
        project = self.SudoProject.create({
            'name': 'Project #2',
            'allow_timesheets': True,
        })
        product = self.SudoProductProduct.create({
            'name': 'Service #2',
            'standard_price': 30,
            'list_price': 90,
            'type': 'service',
            'invoice_policy': 'delivery',
            'uom_id': self.uom_hour.id,
            'uom_po_id': self.uom_hour.id,
            'default_code': 'CODE-2',
            'service_type': 'timesheet',
            'service_tracking': 'task_global_project',
            'project_id': project.id,
            'taxes_id': False,
            'property_account_income_id': account.id,
        })
        role = self.SudoRole.create({
            'name': 'Role #2',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #2',
            'user_id': self.env.user.id,
            'timesheet_cost': 42,
        })
        account_payable = self.SudoAccountAccount.create({
            'code': 'AP4',
            'name': 'Payable #2',
            'user_type_id': self.user_type_payable.id,
            'reconcile': True,
        })
        account_receivable = self.SudoAccountAccount.create({
            'code': 'AR4',
            'name': 'Receivable #2',
            'user_type_id': self.user_type_receivable.id,
            'reconcile': True
        })
        partner = self.SudoPartner.create({
            'name': 'Partner #2',
            'email': 'partner-2@localhost',
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

        project.write({
            'sale_line_employee_role_ids': [
                (0, 0, {
                    'sale_line_id': sale_order_line.id,
                    'employee_id': employee.id,
                    'role_id': role.id,
                }),
            ],
        })
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            project.write({
                'sale_line_employee_role_ids': [
                    (0, 0, {
                        'sale_line_id': sale_order_line.id,
                        'employee_id': employee.id,
                        'role_id': role.id,
                    }),
                ],
            })

    def test_3(self):
        account = self.SudoAccountAccount.create({
            'code': 'TEST-3',
            'name': 'Sales #3',
            'reconcile': True,
            'user_type_id': self.user_type_revenue.id,
        })
        project = self.SudoProject.create({
            'name': 'Project #3',
            'allow_timesheets': True,
        })
        product = self.SudoProductProduct.create({
            'name': 'Service #3',
            'standard_price': 30,
            'list_price': 90,
            'type': 'service',
            'invoice_policy': 'delivery',
            'uom_id': self.uom_hour.id,
            'uom_po_id': self.uom_hour.id,
            'default_code': 'CODE-3',
            'service_type': 'timesheet',
            'service_tracking': 'task_global_project',
            'project_id': project.id,
            'taxes_id': False,
            'property_account_income_id': account.id,
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #3',
            'user_id': self.env.user.id,
            'timesheet_cost': 42,
        })
        account_payable = self.SudoAccountAccount.create({
            'code': 'AP4',
            'name': 'Payable #3',
            'user_type_id': self.user_type_payable.id,
            'reconcile': True,
        })
        account_receivable = self.SudoAccountAccount.create({
            'code': 'AR4',
            'name': 'Receivable #3',
            'user_type_id': self.user_type_receivable.id,
            'reconcile': True
        })
        partner = self.SudoPartner.create({
            'name': 'Partner #3',
            'email': 'partner-3@localhost',
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

        project.write({
            'sale_line_employee_role_ids': [
                (0, 0, {
                    'sale_line_id': sale_order_line.id,
                    'employee_id': employee.id,
                }),
            ],
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            project.write({
                'sale_line_employee_role_ids': [
                    (0, 0, {
                        'sale_line_id': sale_order_line.id,
                        'employee_id': employee.id,
                    }),
                ],
            })

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
        role = self.SudoRole.create({
            'name': 'Role #4',
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
            'email': 'partner-4@localhost',
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

        project.write({
            'sale_line_employee_role_ids': [
                (0, 0, {
                    'sale_line_id': sale_order_line.id,
                    'role_id': role.id,
                }),
            ],
        })
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            project.write({
                'sale_line_employee_role_ids': [
                    (0, 0, {
                        'sale_line_id': sale_order_line.id,
                        'role_id': role.id,
                    }),
                ],
            })

    def test_5(self):
        proxied_billable_type = self.SudoProject._fields[
            'proxied_billable_type'
        ]
        selection = proxied_billable_type.selection
        if (callable(selection)):
            selection = selection(self.SudoProject)
        self.assertTrue(any(x[0] == 'employee_role_rate' for x in selection))

    def test_6(self):
        account_payable = self.SudoAccountAccount.create({
            'code': 'AP6',
            'name': 'Payable #6',
            'user_type_id': self.user_type_payable.id,
            'reconcile': True,
        })
        account_receivable = self.SudoAccountAccount.create({
            'code': 'AR6',
            'name': 'Receivable #6',
            'user_type_id': self.user_type_receivable.id,
            'reconcile': True
        })
        partner = self.SudoPartner.create({
            'name': 'Partner #6',
            'email': 'partner-6@localhost',
            'customer': True,
            'property_account_payable_id': account_payable.id,
            'property_account_receivable_id': account_receivable.id,
        })
        project = self.SudoProject.create({
            'name': 'Project #6',
            'allow_timesheets': True,
            'billable_type': 'no',
            'partner_id': partner.id,
        })
        task = self.SudoTask.with_context(
            default_project_id=project.id,
        ).create({
            'name': 'Task #6-1',
            'partner_id': partner.id,
            'planned_hours': 10,
        })
        role_1 = self.SudoRole.create({
            'name': 'Role #6-1',
        })
        role_2 = self.SudoRole.create({
            'name': 'Role #6-2',
        })
        role_3 = self.SudoRole.create({
            'name': 'Role #6-3',
        })
        role_4 = self.SudoRole.create({
            'name': 'Role #6-4',
        })
        employee_1 = self.SudoEmployee.create({
            'name': 'Employee #6-1',
            'user_id': self.env.user.id,
        })
        employee_2 = self.SudoEmployee.create({
            'name': 'Employee #6-2',
            'user_id': self.env.user.id,
        })
        timesheet_1 = self.SudoAccountAnalyticLine.create({
            'name': 'Timesheet #6-1 (no role)',
            'project_id': project.id,
            'task_id': task.id,
            'unit_amount': 3,
            'employee_id': employee_1.id,
        })
        timesheet_2 = self.SudoAccountAnalyticLine.create({
            'name': 'Timesheet #6-2 (role #6-1)',
            'project_id': project.id,
            'task_id': task.id,
            'unit_amount': 2,
            'employee_id': employee_1.id,
            'role_id': role_1.id,
        })
        timesheet_3 = self.SudoAccountAnalyticLine.create({
            'name': 'Timesheet #6-3 (role #6-2)',
            'project_id': project.id,
            'task_id': task.id,
            'unit_amount': 1,
            'employee_id': employee_2.id,
            'role_id': role_2.id,
        })
        timesheet_4 = self.SudoAccountAnalyticLine.create({
            'name': 'Timesheet #6-4 (role #6-3)',
            'project_id': project.id,
            'task_id': task.id,
            'unit_amount': 5,
            'employee_id': employee_2.id,
            'role_id': role_3.id,
        })
        timesheet_5 = self.SudoAccountAnalyticLine.create({
            'name': 'Timesheet #6-5 (role #6-4)',
            'project_id': project.id,
            'task_id': task.id,
            'unit_amount': 5,
            'employee_id': employee_2.id,
            'role_id': role_4.id,
        })
        account = self.SudoAccountAccount.create({
            'code': 'TEST-6',
            'name': 'Sales #6',
            'reconcile': True,
            'user_type_id': self.user_type_revenue.id,
        })
        product = self.SudoProductProduct.create({
            'name': 'Service #6',
            'standard_price': 30,
            'list_price': 90,
            'type': 'service',
            'invoice_policy': 'delivery',
            'uom_id': self.uom_hour.id,
            'uom_po_id': self.uom_hour.id,
            'default_code': 'CODE-6',
            'service_type': 'timesheet',
            'service_tracking': 'no',
            'project_id': False,
            'taxes_id': False,
            'property_account_income_id': account.id,
        })
        wizard = self.ProjectCreateSaleOrder.with_context(
            active_id=project.id,
            active_model='project.project',
        ).create({
            'billable_type': 'employee_role_rate',
            'partner_id': partner.id,
            'employee_role_ids': [
                (0, 0, {
                    'product_id': product.id,
                    'price_unit': 142,
                    'employee_id': employee_1.id,
                }),
                (0, 0, {
                    'product_id': product.id,
                    'price_unit': 242,
                    'employee_id': employee_1.id,
                    'role_id': role_1.id,
                }),
                (0, 0, {
                    'product_id': product.id,
                    'price_unit': 342,
                    'role_id': role_2.id,
                }),
                (0, 0, {
                    'product_id': product.id,
                    'price_unit': 442,
                    'employee_id': employee_1.id,
                    'role_id': role_3.id,
                }),
                (0, 0, {
                    'product_id': product.id,
                    'price_unit': 542,
                    'role_id': role_4.id,
                }),
            ]
        })

        self.assertEqual(project.billable_type, 'no')
        self.assertEqual(wizard.partner_id, project.partner_id)
        self.assertEqual(wizard.project_id, project)

        # create the SO from the project
        action = wizard.action_create_sale_order()
        sale_order = self.SudoSaleOrder.browse(action['res_id'])

        self.assertEqual(project.billable_type, 'employee_role_rate')
        self.assertEqual(sale_order.partner_id, project.partner_id)
        self.assertEqual(len(sale_order.order_line), 5)
        self.assertEqual(len(project.sale_line_employee_role_ids), 5)
        self.assertEqual(project.sale_line_id, sale_order.order_line[0])
        self.assertEqual(task.sale_line_id, sale_order.order_line[0])
        self.assertEqual(task.partner_id, wizard.partner_id)

        line_1 = sale_order.order_line.filtered(
            lambda sol: sol.price_unit == 142
        )
        self.assertEqual(timesheet_1.so_line, line_1)
        self.assertEqual(line_1.qty_delivered, timesheet_1.unit_amount)

        line_2 = sale_order.order_line.filtered(
            lambda sol: sol.price_unit == 242
        )
        self.assertEqual(timesheet_2.so_line, line_2)
        self.assertEqual(line_2.qty_delivered, timesheet_2.unit_amount)

        line_3 = sale_order.order_line.filtered(
            lambda sol: sol.price_unit == 342
        )
        self.assertEqual(timesheet_3.so_line, line_3)
        self.assertEqual(line_3.qty_delivered, timesheet_3.unit_amount)

        line_4 = sale_order.order_line.filtered(
            lambda sol: sol.price_unit == 442
        )
        self.assertEqual(timesheet_4.so_line.id, False)
        self.assertEqual(line_4.qty_delivered, 0)

        line_5 = sale_order.order_line.filtered(
            lambda sol: sol.price_unit == 542
        )
        self.assertEqual(timesheet_5.so_line, line_5)
        self.assertEqual(line_5.qty_delivered, timesheet_5.unit_amount)

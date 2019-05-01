# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestSaleTimesheetProjectBillingTypeManual(common.TransactionCase):

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

        self.assertFalse(project.proxied_billable_type)
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
        project._onchange_sale_line_employee_ids()
        self.assertEqual(project.billable_type, 'employee_rate')

        project.manual_billable_type = False
        self.assertEqual(project.billable_type, 'task_rate')
        self.assertEqual(project.proxied_billable_type, 'task_rate')
        project._onchange_sale_line_employee_ids()
        self.assertEqual(project.billable_type, 'task_rate')

        project.proxied_billable_type = 'employee_rate'
        self.assertEqual(project.billable_type, 'employee_rate')
        self.assertEqual(project.manual_billable_type, 'employee_rate')
        project._onchange_sale_line_employee_ids()
        self.assertEqual(project.billable_type, 'employee_rate')

        project.proxied_billable_type = False
        self.assertEqual(project.billable_type, 'task_rate')
        self.assertEqual(project.manual_billable_type, False)
        project._onchange_sale_line_employee_ids()
        self.assertEqual(project.billable_type, 'task_rate')

        project.proxied_billable_type = 'employee_rate'
        project.proxied_billable_type = False
        project._onchange_proxied_billable_type()
        self.assertEqual(project.proxied_billable_type, 'task_rate')
        project._onchange_sale_line_employee_ids()
        self.assertEqual(project.proxied_billable_type, 'task_rate')

        project.proxied_billable_type = 'task_rate'
        self.assertEqual(project.manual_billable_type, 'task_rate')
        task = self.SudoProjectTask.create({
            'name': 'ProjectTask #3',
            'project_id': project.id,
        })
        task._onchange_project()
        self.assertEqual(task.billable_type, 'task_rate')

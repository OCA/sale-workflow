# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestSaleTimesheetProjectManual(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleTimesheetProjectManual, cls).setUpClass()
        cls.Product = cls.env['product.product']
        cls.SaleOrder = cls.env['sale.order']

        cls.partner_agrolait = cls.env.ref('base.res_partner_2')
        cls.uom_unit_wt = cls.env.ref('product.uom_categ_wtime')

        cls.product_service_task = cls.Product.create({
            'name': "Service (with task)",
            'type': "service",
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_new_project',
            'uom_id': cls.uom_unit_wt.id,
            'uom_po_id': cls.uom_unit_wt.id,
        })

        cls.product_service_project = cls.Product.create({
            'name': "Service (only project)",
            'type': "service",
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'project_only',
            'uom_id': cls.uom_unit_wt.id,
            'uom_po_id': cls.uom_unit_wt.id,
        })

    def test_01_project_manual(self):
        order = self.SaleOrder.create({
            'partner_id': self.partner_agrolait.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_service_task.id,
                    'name': "Task 1",
                    'product_uom_qty': 10,
                    'product_uom': self.uom_unit_wt.id,
                }),
                (0, 0, {
                    'product_id': self.product_service_task.id,
                    'name': "Task 2",
                    'product_uom_qty': 15,
                    'product_uom': self.uom_unit_wt.id,
                }),
                (0, 0, {
                    'product_id': self.product_service_project.id,
                    'name': "Task (Misc)",
                    'product_uom_qty': 15,
                    'product_uom': self.uom_unit_wt.id,
                })
            ]
        })

        self.assertTrue(order.action_project_manual_allowed)
        order.action_cancel()

        self.assertFalse(order.action_project_manual_allowed)
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            order.action_project_manual()

        order.action_draft()
        self.assertTrue(order.action_project_manual_allowed)

        order.action_project_manual()
        analytic_account = order.analytic_account_id
        self.assertTrue(order.name in analytic_account.name)

        projects = analytic_account.project_ids
        line_tasks = order.order_line.mapped('task_id')

        self.assertEqual(len(projects), 1)
        self.assertEqual(len(line_tasks), 2)

        self.assertEqual(
            line_tasks.mapped('project_id'),
            projects)

        order.action_confirm()
        self.assertFalse(order.action_project_manual_allowed)
        order.invalidate_cache()

        analytic_account_1 = order.analytic_account_id
        projects_1 = analytic_account.project_ids
        line_tasks_1 = order.order_line.mapped('task_id')

        self.assertEqual(analytic_account_1, analytic_account)
        self.assertEqual(projects_1, projects)
        self.assertEqual(line_tasks_1, line_tasks)

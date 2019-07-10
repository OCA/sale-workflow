# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SingleTransactionCase


class TestProjectMilestoneProfileInvoicing(SingleTransactionCase):
    """  """

    @classmethod
    def setUpClass(cls):
        """ Setup sale order and project.

        Create a sale order with 2 milestones product, 2 rates product
        and 1 stockable product.
        Confirm the sale order.
        With the project linked to the sale order
        In project configuration link two employees one to each rate sale
        line.
        """
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.aal_model = cls.env['account.analytic.line']
        cls.product_S1 = cls.env['product.product'].create(
            {
                'name': 'Stockable One',
                'type': 'consu',
                'invoice_policy': 'delivery',
            }
        )
        cls.product_M1 = cls.env['product.product'].create(
            {
                'name': 'Service Milestone One',
                'type': 'service',
                'service_policy': 'delivered_manual',
                'service_tracking': 'task_new_project',
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
            }
        )
        cls.product_R1 = cls.env['product.product'].create(
            {
                'name': 'Service Rate One',
                'type': 'service',
                'service_policy': 'delivered_timesheet',
                'service_tracking': 'no',
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
            }
        )
        cls.product_R2 = cls.product_R1.copy({'name': 'Service Rate Two'})
        cls.employee_junior = cls.env['hr.employee'].create({'name': 'Junior'})
        cls.employee_senior = cls.env['hr.employee'].create({'name': 'Senior'})
        cls.customer = cls.env['res.partner'].create(
            {'name': 'Customer One', 'customer': True}
        )

        cls.so = cls.env['sale.order'].create(
            {
                'partner_id': cls.customer.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'product_id': cls.product_M1.id,
                            'product_uom_qty': 1,
                            'price_unit': 1000,
                            'sequence': 0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'product_id': cls.product_M1.id,
                            'product_uom_qty': 1,
                            'price_unit': 2000,
                            'sequence': 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'product_id': cls.product_R1.id,
                            'product_uom_qty': 0,
                            'price_unit': 100,
                            'sequence': 2,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'product_id': cls.product_R2.id,
                            'product_uom_qty': 0,
                            'price_unit': 200,
                            'sequence': 3,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'product_id': cls.product_S1.id,
                            'product_uom_qty': 2,
                            'price_unit': 500,
                            'sequence': 4,
                        },
                    ),
                ],
            }
        )
        cls.line_M1 = cls.so.order_line.search(
            [('order_id', '=', cls.so.id), ('sequence', '=', 0)]
        )
        cls.line_M2 = cls.so.order_line.search(
            [('order_id', '=', cls.so.id), ('sequence', '=', 1)]
        )
        cls.line_R1 = cls.so.order_line.search(
            [('order_id', '=', cls.so.id), ('sequence', '=', 2)]
        )
        cls.line_R2 = cls.so.order_line.search(
            [('order_id', '=', cls.so.id), ('sequence', '=', 3)]
        )
        cls.line_S1 = cls.so.order_line.search(
            [('order_id', '=', cls.so.id), ('sequence', '=', 4)]
        )
        cls.so.action_confirm()
        cls.project = cls.so.project_ids[0]

        cls.project.sale_line_employee_ids = [
            (
                0,
                0,
                {
                    'employee_id': cls.employee_junior.id,
                    'sale_line_id': cls.so.order_line[2].id,
                },
            ),
            (
                0,
                0,
                {
                    'employee_id': cls.employee_senior.id,
                    'sale_line_id': cls.so.order_line[3].id,
                },
            ),
        ]

        cls.task_M1 = cls.project.task_ids.search(
            [('sale_line_id', '=', cls.so.order_line[0].id)]
        )
        cls.task_M2 = cls.project.task_ids.search(
            [('sale_line_id', '=', cls.so.order_line[1].id)]
        )
        cls.account_type = cls.env['account.account.type'].create(
            {'name': 'Test', 'type': 'receivable'}
        )
        cls.account = cls.env['account.account'].create(
            {
                'name': 'Test account',
                'code': 'TEST',
                'user_type_id': cls.account_type.id,
                'reconcile': True,
            }
        )

    def test_step_1(self):
        """ Timesheet on milestones.

        On both milestones by two different employees profile.
        """
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'employee_id': self.employee_junior.id,
                'name': 'TS Junior on milestone 1',
                'task_id': self.task_M1.id,
                'unit_amount': 6,
            }
        )
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'employee_id': self.employee_senior.id,
                'name': 'TS Senior on milestone 1',
                'task_id': self.task_M1.id,
                'unit_amount': 2,
            }
        )
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'employee_id': self.employee_junior.id,
                'name': 'TS Junior on milestone 2',
                'task_id': self.task_M2.id,
                'unit_amount': 8,
            }
        )
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'employee_id': self.employee_senior.id,
                'name': 'TS Senior on milestone 2',
                'task_id': self.task_M2.id,
                'unit_amount': 4,
            }
        )
        # Analytic line without employee should not change the result
        self.aal_model.create(
            {
                'project_id': self.project.id,
                # 'employee_id': self.employee_senior.id,
                'name': 'TS Senior on milestone 2',
                'task_id': self.task_M2.id,
                'unit_amount': 334,
            }
        )
        self.assertEqual(
            self.line_M1.amount_delivered_from_task, (6 * 100 + 2 * 200)
        )
        self.assertEqual(self.line_M1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_M1.invoice_status, 'no')
        self.assertEqual(self.line_M1.qty_delivered, (1 * 1000 / 1000))
        self.assertEqual(self.line_M1.qty_invoiced, 0)

        self.assertEqual(
            self.line_M2.amount_delivered_from_task, (8 * 100 + 4 * 200)
        )
        self.assertEqual(self.line_M2.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_M2.invoice_status, 'no')
        self.assertEqual(self.line_M2.qty_delivered, (1 * 1600 / 2000))
        self.assertEqual(self.line_M2.qty_invoiced, 0)

        self.assertEqual(self.line_R1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_R1.invoice_status, 'to invoice')
        self.assertEqual(self.line_R1.qty_delivered, 14)
        self.assertEqual(self.line_R1.qty_invoiced, 0)

        self.assertEqual(self.line_R2.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R2.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_R2.invoice_status, 'to invoice')
        self.assertEqual(self.line_R2.qty_delivered, 6)
        self.assertEqual(self.line_R2.qty_invoiced, 0)

        self.assertEqual(self.line_S1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_S1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_S1.invoice_status, 'no')
        self.assertEqual(self.line_S1.qty_delivered, 0)
        self.assertEqual(self.line_S1.qty_invoiced, 0)

    def test_step_2(self):
        """ Create an invoice.

        With a total of 2600.-- targeting both rate products.
        """
        self.invoice = self.env['account.invoice'].create(
            {
                'partner_id': self.customer.id,
                'account_id': self.account.id,
                'invoice_line_ids': [
                    (
                        0,
                        0,
                        {
                            'name': self.product_R1.name,
                            'product_id': self.product_R1.id,
                            'quantity': 14,
                            'uom_id': self.ref('uom.product_uom_unit'),
                            'price_unit': 100,
                            'account_id': self.account.id,
                            'sale_line_ids': [(4, self.line_R1.id, 0)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.product_R2.name,
                            'product_id': self.product_R2.id,
                            'quantity': 6,
                            'uom_id': self.ref('uom.product_uom_unit'),
                            'price_unit': 200,
                            'account_id': self.account.id,
                            'sale_line_ids': [(4, self.line_R2.id, 0)],
                        },
                    ),
                ],
            }
        )
        self.invoice.action_invoice_open()
        self.assertEqual(
            self.line_M1.amount_delivered_from_task, (6 * 100 + 2 * 200)
        )
        self.assertEqual(self.line_M1.amount_invoiced_from_task, 1000)
        self.assertEqual(self.line_M1.invoice_status, 'no')
        self.assertEqual(self.line_M1.qty_delivered, (1 * 1000 / 1000))
        self.assertEqual(self.line_M1.qty_invoiced, 1)

        self.assertEqual(
            self.line_M2.amount_delivered_from_task, (8 * 100 + 4 * 200)
        )
        self.assertEqual(self.line_M2.amount_invoiced_from_task, 1600)
        self.assertEqual(self.line_M2.invoice_status, 'no')
        self.assertEqual(self.line_M2.qty_delivered, (1 * 1600 / 2000))
        self.assertEqual(self.line_M2.qty_invoiced, 0.8)

        self.assertEqual(self.line_R1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R1.amount_invoiced_from_task, 0)
        self.assertEqual(
            self.line_R1.invoice_status, 'invoiced'
        )  # Insted of no ?
        self.assertEqual(self.line_R1.qty_delivered, 14)
        self.assertEqual(self.line_R1.qty_invoiced, 14)

        self.assertEqual(self.line_R2.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R2.amount_invoiced_from_task, 0)
        self.assertEqual(
            self.line_R2.invoice_status, 'invoiced'
        )  # Insted of no ?
        self.assertEqual(self.line_R2.qty_delivered, 6)
        self.assertEqual(self.line_R2.qty_invoiced, 6)

        self.assertEqual(self.line_S1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_S1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_S1.invoice_status, 'no')
        self.assertEqual(self.line_S1.qty_delivered, 0)
        self.assertEqual(self.line_S1.qty_invoiced, 0)

    def test_step_3(self):
        """ Deliver 1 S1 and both employee timesheet more."""
        self.line_S1.qty_delivered = 1
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'employee_id': self.employee_senior.id,
                'name': 'TS Senior on milestone 1',
                'task_id': self.task_M1.id,
                'unit_amount': 1,
            }
        )
        self.aal_model.create(
            {
                'project_id': self.project.id,
                'employee_id': self.employee_junior.id,
                'name': 'TS Junior on milestone 2',
                'task_id': self.task_M2.id,
                'unit_amount': 4,
            }
        )
        self.assertEqual(
            self.line_M1.amount_delivered_from_task,
            (6 * 100 + 2 * 200 + 1 * 200),
        )
        self.assertEqual(self.line_M1.amount_invoiced_from_task, 1000)
        self.assertEqual(self.line_M1.invoice_status, 'upselling')
        self.assertEqual(self.line_M1.qty_delivered, (1.2))
        self.assertEqual(self.line_M1.qty_invoiced, 1)

        self.assertEqual(
            self.line_M2.amount_delivered_from_task,
            (8 * 100 + 4 * 200 + 4 * 100),
        )
        self.assertEqual(self.line_M2.amount_invoiced_from_task, 1600)
        self.assertEqual(self.line_M2.invoice_status, 'no')
        self.assertEqual(self.line_M2.qty_delivered, 1)
        self.assertEqual(self.line_M2.qty_invoiced, 0.8)

        self.assertEqual(self.line_R1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_R1.invoice_status, 'to invoice')
        self.assertEqual(self.line_R1.qty_delivered, 18)
        self.assertEqual(self.line_R1.qty_invoiced, 14)

        self.assertEqual(self.line_R2.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R2.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_R2.invoice_status, 'to invoice')
        self.assertEqual(self.line_R2.qty_delivered, 7)
        self.assertEqual(self.line_R2.qty_invoiced, 6)

        self.assertEqual(self.line_S1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_S1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_S1.invoice_status, 'to invoice')
        self.assertEqual(self.line_S1.qty_delivered, 1)
        self.assertEqual(self.line_S1.qty_invoiced, 0)

    def test_step_4(self):
        """ Create an other invoice.

        Targetting both rate product and the stockable product
        """
        self.invoice = self.env['account.invoice'].create(
            {
                'partner_id': self.customer.id,
                'account_id': self.account.id,
                'invoice_line_ids': [
                    (
                        0,
                        0,
                        {
                            'name': self.product_R1.name,
                            'product_id': self.product_R1.id,
                            'quantity': 4,
                            'uom_id': self.ref('uom.product_uom_unit'),
                            'price_unit': 100,
                            'account_id': self.account.id,
                            'sale_line_ids': [(4, self.line_R1.id, 0)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.product_R2.name,
                            'product_id': self.product_R2.id,
                            'quantity': 1,
                            'uom_id': self.ref('uom.product_uom_unit'),
                            'price_unit': 200,
                            'account_id': self.account.id,
                            'sale_line_ids': [(4, self.line_R2.id, 0)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.product_S1.name,
                            'product_id': self.product_S1.id,
                            'quantity': 1,
                            'uom_id': self.ref('uom.product_uom_unit'),
                            'price_unit': 500,
                            'account_id': self.account.id,
                            'sale_line_ids': [(4, self.line_S1.id, 0)],
                        },
                    ),
                ],
            }
        )
        self.invoice.action_invoice_open()
        self.assertEqual(self.line_M1.amount_delivered_from_task, (1200))
        self.assertEqual(self.line_M1.amount_invoiced_from_task, 1200)
        self.assertEqual(self.line_M1.invoice_status, 'upselling')
        self.assertEqual(self.line_M1.qty_delivered, 1.2)
        self.assertEqual(self.line_M1.qty_invoiced, 1.2)

        self.assertEqual(self.line_M2.amount_delivered_from_task, 2000)
        self.assertEqual(self.line_M2.amount_invoiced_from_task, 2000)
        self.assertEqual(self.line_M2.invoice_status, 'no')
        self.assertEqual(self.line_M2.qty_delivered, 1)
        self.assertEqual(self.line_M2.qty_invoiced, 1)

        self.assertEqual(self.line_R1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_R1.invoice_status, 'invoiced')
        self.assertEqual(self.line_R1.qty_delivered, 18)
        self.assertEqual(self.line_R1.qty_invoiced, 18)

        self.assertEqual(self.line_R2.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R2.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_R2.invoice_status, 'invoiced')
        self.assertEqual(self.line_R2.qty_delivered, 7)
        self.assertEqual(self.line_R2.qty_invoiced, 7)

        self.assertEqual(self.line_S1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_S1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_S1.invoice_status, 'no')
        self.assertEqual(self.line_S1.qty_delivered, 1)
        self.assertEqual(self.line_S1.qty_invoiced, 1)

    def test_step_5(self):
        """ Change unit price of both milestone in the sale order.
        """
        self.line_M1.price_unit = 1400
        self.line_M2.price_unit = 2400
        self.assertEqual(self.line_M1.amount_delivered_from_task, (1200))
        self.assertEqual(self.line_M1.amount_invoiced_from_task, 1200)
        self.assertEqual(self.line_M1.invoice_status, 'no')
        self.assertEqual(round(self.line_M1.qty_delivered, 2), 0.86)
        self.assertEqual(round(self.line_M1.qty_invoiced, 2), 0.86)

        self.assertEqual(self.line_M2.amount_delivered_from_task, 2000)
        self.assertEqual(self.line_M2.amount_invoiced_from_task, 2000)
        self.assertEqual(self.line_M2.invoice_status, 'no')
        self.assertEqual(round(self.line_M2.qty_delivered, 2), 0.83)
        self.assertEqual(round(self.line_M2.qty_invoiced, 2), 0.83)

        self.assertEqual(self.line_R1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_R1.invoice_status, 'invoiced')
        self.assertEqual(self.line_R1.qty_delivered, 18)
        self.assertEqual(self.line_R1.qty_invoiced, 18)

        self.assertEqual(self.line_R2.amount_delivered_from_task, 0)
        self.assertEqual(self.line_R2.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_R2.invoice_status, 'invoiced')
        self.assertEqual(self.line_R2.qty_delivered, 7)
        self.assertEqual(self.line_R2.qty_invoiced, 7)

        self.assertEqual(self.line_S1.amount_delivered_from_task, 0)
        self.assertEqual(self.line_S1.amount_invoiced_from_task, 0)
        self.assertEqual(self.line_S1.invoice_status, 'no')
        self.assertEqual(self.line_S1.qty_delivered, 1)
        self.assertEqual(self.line_S1.qty_invoiced, 1)

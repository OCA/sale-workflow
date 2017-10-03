# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSaleProjectUserProfile(TransactionCase):

    def setUp(self):
        super(TestSaleProjectUserProfile, self).setUp()

        self.partner = self.env['res.partner'].create({
            'name': 'Unittest partner',
        })

        self.product_model = self.env['product.product']
        self.product_service_user_profile_1 = self.product_model.create({
            'name': 'Unittest Service User Profile 1',
            'type': 'service',
            'track_service': 'user_profile',
        })
        self.product_service_user_profile_2 = self.product_model.create({
            'name': 'Unittest Service User Profile 2',
            'type': 'service',
            'track_service': 'user_profile',
        })
        self.product_service_timesheet = self.product_model.create({
            'name': 'Unittest Service Timesheet',
            'type': 'service',
            'track_service': 'timesheet',
        })
        self.product_service_other = self.product_model.create({
            'name': 'Unittest Service Other',
            'type': 'service',
            'track_service': 'manual',
        })
        self.product_consumable = self.product_model.create({
            'name': 'Unittest Consumable',
        })

        self.user_model = self.env['res.users']
        self.user_1 = self.user_model.create({
            'name': 'Unittest User 1',
            'login': 'user_1',
        })
        self.user_2 = self.user_model.create({
            'name': 'Unittest User 2',
            'login': 'user_2',
        })

    def create_sale_order(self, lines):
        order_line = []
        for product, quantity in lines:
            order_line.append(
                (0, False, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': quantity,
                    'product_uom': self.ref('product.product_uom_unit'),
                }),
            )
        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': order_line,
        })
        for line in sale.order_line:
            line.product_id_change()
        return sale

    def create_task_on_project(self, project, task_name):
        return self.env['project.task'].create({
            'project_id': project.id,
            'name': task_name
        })

    def create_timesheet_line(self, user, project, task, amount):
        return self.env['account.analytic.line'].create({
            'user_id': user.id,
            'project_id': project.id,
            'task_id': task.id,
            'unit_amount': amount,
            'name': 'test',
        })

    def test_01_sale_state_constraints(self):
        # We want to test that you can confirm sale order which
        # have a service product 'User profile' and another service product
        values_for_test = [
            ([
                (self.product_service_user_profile_1, 10),
            ], False),
            ([
                (self.product_service_timesheet, 10),
            ], False),
            ([
                (self.product_service_other, 10),
            ], False),
            ([
                (self.product_consumable, 10),
            ], False),
            ([
                (self.product_service_user_profile_1, 10),
                (self.product_service_user_profile_2, 10),
            ], False),
            ([
                (self.product_service_user_profile_1, 10),
                (self.product_consumable, 10),
            ], False),
            ([
                (self.product_service_user_profile_1, 10),
                (self.product_service_timesheet, 10),
            ], True),
            ([
                (self.product_service_user_profile_1, 10),
                (self.product_service_other, 10),
            ], True),
        ]
        for lines, raise_exception in values_for_test:
            sale = self.create_sale_order(lines)
            if not raise_exception:
                sale.action_confirm()
            else:
                with self.assertRaises(ValidationError):
                    sale.action_confirm()

    def test_02_timesheet_no_regression_on_non_user_profile_service(self):
        # With a project created from a sale order with user profile service,
        # we can't create timesheet without specific mapping on project.
        #
        # Here, we test if with another service product,
        # we can create timesheet without problem.
        sale = self.create_sale_order([
            (self.product_service_timesheet, 10),
        ])
        sale.action_confirm()

        project = sale.project_id.project_ids

        self.assertEqual(len(project), 1)
        self.assertEqual(len(project.task_ids), 0)

        task_1 = self.create_task_on_project(project, 'task 1')

        self.create_timesheet_line(self.user_1, project, task_1, 1)

    def test_03_project_user_task_sale_line_mapping_constraint(self):
        # test constraint on project user task sale line mapping
        sale = self.create_sale_order([
            (self.product_service_user_profile_1, 10),
            (self.product_service_user_profile_2, 10),
        ])
        sale.action_confirm()

        project = sale.project_id.project_ids

        self.assertEqual(len(project), 1)
        self.assertEqual(len(project.task_ids), 0)

        task_1 = self.create_task_on_project(project, 'task 1')
        task_2 = self.create_task_on_project(project, 'task 2')

        values_for_test = [
            ([
                (self.user_1.id, False, sale.order_line[0].id),
            ], False),
            ([
                (self.user_1.id, False, sale.order_line[0].id),
                (self.user_1.id, False, sale.order_line[0].id),
            ], True),
            ([
                (self.user_1.id, task_1.id, sale.order_line[0].id),
            ], False),
            ([
                (self.user_1.id, False, sale.order_line[0].id),
                (self.user_1.id, task_1.id, sale.order_line[0].id),
            ], False),
            ([
                (self.user_1.id, task_1.id, sale.order_line[0].id),
                (self.user_1.id, task_1.id, sale.order_line[0].id),
            ], True),
            ([
                (self.user_1.id, task_1.id, sale.order_line[0].id),
                (self.user_1.id, task_1.id, sale.order_line[1].id),
            ], True),
            ([
                (self.user_1.id, task_1.id, sale.order_line[0].id),
                (self.user_1.id, task_2.id, sale.order_line[0].id),
            ], False),
            ([
                (self.user_1.id, task_1.id, sale.order_line[0].id),
                (self.user_2.id, task_1.id, sale.order_line[0].id),
            ], False),
        ]
        for mapping, raise_exception in values_for_test:
            project.project_user_task_sale_line_map_ids.unlink()

            project_user_task_sale_line_map_ids = []
            for user_id, task_id, sale_line_id in mapping:
                project_user_task_sale_line_map_ids.append(
                    (0, False, {
                        'user_id': user_id,
                        'task_id': task_id,
                        'sale_line_id': sale_line_id,
                    }),
                )
            if not raise_exception:
                project.write({
                    'project_user_task_sale_line_map_ids':
                        project_user_task_sale_line_map_ids,
                })
            else:
                with self.assertRaises(ValidationError):
                    project.write({
                        'project_user_task_sale_line_map_ids':
                            project_user_task_sale_line_map_ids,
                    })

    def test_04_project_user_task_sale_line_mapping(self):
        # Test all cases of mapping
        sale = self.create_sale_order([
            (self.product_service_user_profile_1, 10),
            (self.product_service_user_profile_2, 10),
        ])
        sale.action_confirm()

        project = sale.project_id.project_ids

        self.assertEqual(len(project), 1)
        self.assertEqual(len(project.task_ids), 0)

        task_1 = self.create_task_on_project(project, 'task 1')
        task_2 = self.create_task_on_project(project, 'task 2')

        with self.assertRaises(ValidationError):
            # At this time, we don't have mapping,
            # so we can't create a timesheet line
            self.create_timesheet_line(self.user_1, project, task_1, 1)

        project.write({
            'project_user_task_sale_line_map_ids': [
                (0, False, {
                    'user_id': self.user_2.id,
                    'task_id': False,
                    'sale_line_id': sale.order_line[0].id,
                }),
            ]
        })

        with self.assertRaises(ValidationError):
            # We can't create a timesheet line
            # because we don't have mapping for this user
            self.create_timesheet_line(self.user_1, project, task_1, 1)

        # Change the user on the mapping
        project.project_user_task_sale_line_map_ids[0].user_id = self.user_1.id

        # With a mapping on the user it's good
        self.create_timesheet_line(self.user_1, project, task_1, 1)

        # We check the qty_delivered have correctly decreased
        self.assertEqual(sale.order_line[0].qty_delivered, 1)

        # Change the task on the mapping
        project.project_user_task_sale_line_map_ids[0].task_id = task_2.id

        with self.assertRaises(ValidationError):
            # We can't create a timesheet line
            # because we don't have mapping for this task
            self.create_timesheet_line(self.user_1, project, task_1, 1)

        # With a mapping on the task it's good
        self.create_timesheet_line(self.user_1, project, task_2, 1)
        self.assertEqual(sale.order_line[0].qty_delivered, 2)

        # Change the sale order line on the mapping
        project.project_user_task_sale_line_map_ids[0].sale_line_id = (
            sale.order_line[1].id
        )

        # We test to create timesheet with mapping on the other sale order line
        self.create_timesheet_line(self.user_1, project, task_2, 1)
        self.assertEqual(sale.order_line[0].qty_delivered, 2)
        self.assertEqual(sale.order_line[1].qty_delivered, 1)

        with self.assertRaises(ValidationError):
            # We can't create a timesheet line
            # because we don't have mapping for this user
            self.create_timesheet_line(self.user_2, project, task_2, 1)

        # Change the user on the mapping
        project.project_user_task_sale_line_map_ids[0].user_id = self.user_2.id

        # We test to create timesheet with other user
        self.create_timesheet_line(self.user_2, project, task_2, 1)
        self.assertEqual(sale.order_line[0].qty_delivered, 2)
        self.assertEqual(sale.order_line[1].qty_delivered, 2)

        with self.assertRaises(ValidationError):
            # We can't create a timesheet line
            # because we don't have mapping for this user
            self.create_timesheet_line(self.user_1, project, task_2, 1)

        # Add a mapping for the user but on the bad task
        project.write({
            'project_user_task_sale_line_map_ids': [
                (0, False, {
                    'user_id': self.user_1.id,
                    'task_id': task_1.id,
                    'sale_line_id': sale.order_line[0].id,
                }),
            ]
        })

        with self.assertRaises(ValidationError):
            # We can't create a timesheet line
            # because we don't have mapping for this user and task
            self.create_timesheet_line(self.user_1, project, task_2, 1)

        # Do a mapping for this user with all task
        project.project_user_task_sale_line_map_ids[1].task_id = False

        # We test to create timesheet with good mapping
        self.create_timesheet_line(self.user_1, project, task_2, 1)
        self.assertEqual(sale.order_line[0].qty_delivered, 3)
        self.assertEqual(sale.order_line[1].qty_delivered, 2)

        # Add a specific mapping for the task but on the other sale order line
        project.write({
            'project_user_task_sale_line_map_ids': [
                (0, False, {
                    'user_id': self.user_1.id,
                    'task_id': task_2.id,
                    'sale_line_id': sale.order_line[1].id,
                }),
            ]
        })

        # We test to create timesheet with the other sale order line
        self.create_timesheet_line(self.user_1, project, task_2, 1)
        self.assertEqual(sale.order_line[0].qty_delivered, 3)
        self.assertEqual(sale.order_line[1].qty_delivered, 3)

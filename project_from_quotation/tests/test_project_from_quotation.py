# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProjectFromQuotation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task_template = cls.env["project.task"].create(
            {
                "name": "Task Template",
                "sequence": 1,
                "planned_hours": 20.0,
                "project_id": cls.env.ref("project.project_project_1").id,
            }
        )
        cls.env["ir.config_parameter"].set_param(
            "project_from_quotation.template_task_id", cls.task_template.id
        )
        cls.env["ir.config_parameter"].set_param(
            "project_from_quotation.template_project_id", 0
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_2").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_4").id,
                            "product_uom_qty": 1,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "price_unit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_4").id,
                            "product_uom_qty": 2,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "price_unit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_5").id,
                            "product_uom_qty": 2,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )

    def test_create_empty_project(self):
        # Create project from quotation without task template
        project = (
            self.env["project.from.quotation"]
            .create(
                {
                    "sale_order_id": self.sale_order.id,
                    "mode": "project",
                }
            )
            .action_create_project()
        )
        # Check if project name is eqiuvalent to sale order name
        self.assertEqual(project.name, self.sale_order.name)
        # Check if project has no tasks
        self.assertFalse(project.task_ids)

    def test_create_project_tasks_per_line(self):
        # Create project with tasks per line using task template
        project = (
            self.env["project.from.quotation"]
            .create(
                {
                    "sale_order_id": self.sale_order.id,
                    "mode": "tasks_per_line",
                }
            )
            .action_create_project()
        )
        # Check if project has 3 tasks
        self.assertEqual(len(project.task_ids), 3)

        # Check if every task has correct name and
        # inherited planned hours from task template

        self.assertTrue(
            all(
                [
                    task.name == line.name
                    and task.planned_hours == self.task_template.planned_hours
                    for line, task in zip(
                        self.sale_order.order_line.sorted("name"),
                        project.task_ids.sorted("name"),
                    )
                ]
            )
        )

    def test_create_project_tasks_per_product(self):
        # Create project with tasks per product using task template
        project = (
            self.env["project.from.quotation"]
            .create(
                {
                    "sale_order_id": self.sale_order.id,
                    "mode": "tasks_per_product",
                }
            )
            .action_create_project()
        )
        # Check if project has 2 tasks
        self.assertEqual(len(project.task_ids), 2)

        # Check if every task has correct name and
        # inherited planned hours from task template
        self.assertTrue(
            all(
                [
                    task.name == line.name
                    and task.planned_hours == self.task_template.planned_hours
                    for line, task in zip(
                        self.sale_order._get_order_lines_unique_products(
                            self.sale_order.order_line
                        ).sorted("name"),
                        project.task_ids.sorted("name"),
                    )
                ]
            )
        )

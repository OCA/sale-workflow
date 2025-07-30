# Copyright 2017 Tecnativa - Sergio Teruel
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form, new_test_user
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestInvoicefinishedTask(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.hour_uom = cls.env.ref("uom.product_uom_hour")
        cls.env.user.company_id.project_time_mode_id = cls.hour_uom.id
        cls.manager = new_test_user(
            cls.env,
            login="test-manager-user",
            groups="sales_team.group_sale_manager",
        )
        cls.employee = cls.env["hr.employee"].create(
            {"name": cls.manager.name, "user_id": cls.manager.id}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Customer - test", "customer_rank": True}
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Some test project",
                "allow_billable": True,
            }
        )
        cls.stage_new = cls.env["project.task.type"].create(cls._prepare_stage_vals())
        cls.stage_invoiceable = cls.env["project.task.type"].create(
            cls._prepare_stage_vals(invoiceable_stage=True)
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.Product = cls.env["product.product"]
        product_vals = cls._prepare_product_vals()
        cls.product = cls.Product.create(product_vals)
        product_delivery_vals = product_vals
        product_delivery_vals.update(
            {
                "name": "Product - Service - Policy delivery - Test",
                "service_policy": "delivered_timesheet",
                "invoice_policy": "delivery",
                "service_type": "timesheet",
            }
        )
        cls.product_policy_delivery = cls.Product.create(product_delivery_vals)
        cls.sale_order = cls.env["sale.order"].create(cls._sale_order_vals(cls.product))
        cls.sale_order_policy_delivery = cls.env["sale.order"].create(
            cls._sale_order_vals(cls.product_policy_delivery)
        )

    @classmethod
    def _prepare_stage_vals(cls, invoiceable_stage=False):
        return {
            "name": "Test Invoiceable",
            "sequence": 5,
            "project_ids": [Command.set(cls.project.ids)],
            "invoiceable": invoiceable_stage,
        }

    @classmethod
    def _sale_order_vals(cls, product):
        return {
            "partner_id": cls.partner.id,
            "pricelist_id": cls.partner.property_product_pricelist.id,
            "order_line": [
                Command.create(
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": 5,
                        "product_uom": product.uom_id.id,
                        "price_unit": product.list_price,
                    },
                ),
            ],
        }

    @classmethod
    def _prepare_product_vals(cls):
        return {
            "name": "Product - Service  - Test",
            "type": "service",
            "list_price": 100.00,
            "standard_price": 50.00,
            "invoice_policy": "order",
            "service_policy": "delivered_timesheet",
            "service_tracking": "task_global_project",
            "invoicing_finished_task": True,
            "project_id": cls.project.id,
            "uom_id": cls.hour_uom.id,
            "uom_po_id": cls.hour_uom.id,
        }

    def _prepare_timesheet_vals(self, task, unit_amount):
        return {
            "name": "Test Line",
            "project_id": self.project.id,
            "unit_amount": unit_amount,
            "product_uom_id": task.sale_line_id.product_uom.id,
            "user_id": self.manager.id,
            "task_id": task.id,
        }

    @mute_logger("odoo.models.unlink")
    def test_invoice_status(self):
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.invoice_status, "no")
        task = self.sale_order.order_line.task_ids
        self.assertFalse(task.invoiceable)
        # Add a timesheet line
        timesheet = self.env["account.analytic.line"].create(
            self._prepare_timesheet_vals(task, 5.0)
        )
        # Set task in invoiceable stage
        task_form = Form(task)
        task_form.stage_id = self.stage_invoiceable
        task = task_form.save()
        self.assertTrue(task.invoiceable)
        self.assertEqual(self.sale_order.invoice_status, "to invoice")
        # delete timesheet
        timesheet.unlink()
        self.assertEqual(self.sale_order.invoice_status, "no")
        # Add another timesheet line
        self.env["account.analytic.line"].create(
            self._prepare_timesheet_vals(task, 10.0)
        )
        self.sale_order.order_line._compute_invoice_status()
        self.assertTrue(task.invoiceable)
        self.assertEqual(self.sale_order.invoice_status, "to invoice")
        # Click on toggle_invoiceable method (invoiceable=False)
        task.toggle_invoiceable()
        self.assertFalse(task.invoiceable)
        self.assertEqual(self.sale_order.invoice_status, "no")
        # Click on toggle_invoiceable method (invoiceable=True)
        task.toggle_invoiceable()
        self.assertTrue(task.invoiceable)
        self.assertEqual(self.sale_order.invoice_status, "to invoice")
        # Make the invoice
        self.sale_order._create_invoices()
        self.assertEqual(self.sale_order.invoice_status, "invoiced")
        # Click on toggle_invoiceable method after the so is invoiced
        with self.assertRaises(ValidationError):
            task.toggle_invoiceable()
        self.sale_order.action_lock()
        with self.assertRaises(ValidationError):
            task.write({"sale_line_id": self.sale_order_policy_delivery.order_line.id})
        # Try to create a task and link it to so line
        with self.assertRaises(ValidationError):
            self.env["project.task"].create(
                {
                    "name": "Other Task",
                    "user_ids": [Command.link(self.manager.id)],
                    "project_id": self.project.id,
                    "sale_line_id": self.sale_order.order_line.id,
                }
            )

    def test_check_qty_to_invoice(self):
        self.sale_order.action_confirm()
        task = self.sale_order.order_line.task_ids
        # Add a timesheet line
        self.env["account.analytic.line"].create(
            self._prepare_timesheet_vals(task, 10.5)
        )
        task.toggle_invoiceable()
        self.assertTrue(task.invoiceable)
        self.assertEqual(self.sale_order.order_line.qty_to_invoice, 5.0)
        self.sale_order_policy_delivery.action_confirm()
        # Add a timesheet line
        task_delivery = self.sale_order_policy_delivery.order_line.task_ids
        self.env["account.analytic.line"].create(
            self._prepare_timesheet_vals(task_delivery, 10.0)
        )
        task_delivery_form = Form(task_delivery)
        task_delivery_form.stage_id = self.stage_invoiceable
        task_delivery = task_delivery_form.save()
        self.assertTrue(task_delivery.invoiceable)
        self.assertEqual(
            self.sale_order_policy_delivery.order_line.qty_to_invoice, 10.0
        )

    def test_create_task_stage_invoiceable(self):
        self.sale_order.action_confirm()
        task = self.env["project.task"].create(
            {
                "name": "Other Task",
                "partner_id": self.manager.id,
                "user_ids": [Command.link(self.manager.id)],
                "project_id": self.project.id,
                "sale_line_id": self.sale_order.order_line.id,
            }
        )
        task_form = Form(task)
        task_form.stage_id = self.stage_invoiceable
        task = task_form.save()
        self.assertTrue(task.invoiceable)

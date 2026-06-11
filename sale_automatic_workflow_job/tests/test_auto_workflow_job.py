# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests import tagged

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.sale_automatic_workflow.tests.common import (
    TestAutomaticWorkflowMixin,
    TestCommon,
)


@tagged("post_install", "-at_install")
class TestAutoWorkflowJob(TestCommon, TestAutomaticWorkflowMixin):
    def create_sale_order(self, workflow, override=None):
        order = super().create_sale_order(workflow, override)
        order.order_line.product_id.invoice_policy = "order"
        return order

    def test_validate_sale_order(self):
        workflow = self.create_full_automatic({"send_order_confirmation_mail": True})
        self.sale = self.create_sale_order(workflow)

        with trap_jobs() as trap:
            self.run_job()  # run automatic workflow cron

            trap.assert_jobs_count(
                1, only=self.env["automatic.workflow.job"]._do_validate_sale_order
            )

            args = (
                self.sale,
                [
                    ("state", "=", "draft"),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )

            trap.assert_enqueued_job(
                self.env["automatic.workflow.job"]._do_validate_sale_order,
                args=args,
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )
            trap.perform_enqueued_jobs()
            trap.assert_jobs_count(
                1,
                only=self.env[
                    "automatic.workflow.job"
                ]._do_send_order_confirmation_mail,
            )

    def test_create_invoice(self):
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)
        self.sale.action_confirm()

        with trap_jobs() as trap:
            self.run_job()  # run automatic workflow cron

            trap.assert_jobs_count(
                1, only=self.env["automatic.workflow.job"]._do_create_invoice
            )

            args = (
                self.sale,
                [
                    ("state", "=", "sale"),
                    ("locked", "=", False),
                    ("invoice_status", "=", "to invoice"),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )

            trap.assert_enqueued_job(
                self.env["automatic.workflow.job"]._do_create_invoice,
                args=args,
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )

    def test_validate_invoice(self):
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)
        self.sale.action_confirm()
        self.sale._create_invoices()
        invoice = self.sale.invoice_ids

        with trap_jobs() as trap:
            self.run_job()  # run automatic workflow cron

            trap.assert_jobs_count(
                1, only=self.env["automatic.workflow.job"]._do_validate_invoice
            )

            args = (
                invoice,
                [
                    ("state", "=", "draft"),
                    ("posted_before", "=", False),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )

            trap.assert_enqueued_job(
                self.env["automatic.workflow.job"]._do_validate_invoice,
                args=args,
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )

    def test_sale_done(self):
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)
        self.sale.action_confirm()
        self.sale._create_invoices()

        # disable invoice validation for we don't care
        # in this test
        self.sale.workflow_process_id.validate_invoice = False
        # activate the 'sale done' workflow
        self.sale.workflow_process_id.sale_done = True

        with trap_jobs() as trap:
            self.run_job()  # run automatic workflow cron

            trap.assert_jobs_count(
                1, only=self.env["automatic.workflow.job"]._do_sale_done
            )

            args = (
                self.sale,
                [
                    ("state", "=", "sale"),
                    ("locked", "=", False),
                    ("invoice_status", "=", "invoiced"),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )

            trap.assert_enqueued_job(
                self.env["automatic.workflow.job"]._do_sale_done,
                args=args,
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )

    def test_job_prepare_context_before_enqueue_keys(self):
        context_keys = self.env[
            "automatic.workflow.job"
        ]._job_prepare_context_before_enqueue_keys()
        self.assertIn("send_order_confirmation_mail_in_job", context_keys)
        self.assertIn("auto_delay_do_send_mail", context_keys)
        self.assertIn("auto_delay_do_validation_finished", context_keys)

    def test_get_register_hook_mapping(self):
        mapping = self.env["automatic.workflow.job"]._get_register_hook_mapping()
        self.assertDictEqual(
            mapping,
            {
                "_do_validate_sale_order": "auto_delay_do_validation",
                "_do_send_order_confirmation_mail": "auto_delay_do_send_mail",
                "_do_create_invoice": "auto_delay_do_create_invoice",
                "_do_validate_invoice": "auto_delay_do_validation",
                "_do_sale_done": "auto_delay_do_sale_done",
            },
        )

    def test_do_send_order_confirmation_mail_without_context(self):
        workflow = self.create_full_automatic({"send_order_confirmation_mail": True})
        sale = self.create_sale_order(workflow)
        result = self.env["automatic.workflow.job"]._do_send_order_confirmation_mail(
            sale
        )
        self.assertIsNone(result)

    def test_related_action_sale_automatic_workflow(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        queue_job_model = self.env["queue.job"]
        method = type(queue_job_model)._related_action_sale_automatic_workflow
        fake_job = mock.Mock(args=[sale], env=self.env)
        action = method(fake_job)

        self.assertEqual(action["name"], "Sale Automatic Workflow Job")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], sale._name)
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["res_id"], sale.id)

    def test_job_options_validate_sale_order(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        options = self.env[
            "automatic.workflow.job"
        ]._do_validate_sale_order_job_options(sale, [])

        self.assertEqual(options["identity_key"], identity_exact)
        self.assertIn(sale.display_name, options["description"])

    def test_job_options_send_order_confirmation_mail(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        options = self.env[
            "automatic.workflow.job"
        ]._do_send_order_confirmation_mail_job_options(sale)

        self.assertEqual(options["identity_key"], identity_exact)
        self.assertIn(sale.display_name, options["description"])

    def test_job_options_create_invoice_validate_invoice_sale_done(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale.action_confirm()
        sale._create_invoices()
        invoice = sale.invoice_ids

        create_invoice_options = self.env[
            "automatic.workflow.job"
        ]._do_create_invoice_job_options(sale, [])
        validate_invoice_options = self.env[
            "automatic.workflow.job"
        ]._do_validate_invoice_job_options(invoice, [])
        sale_done_options = self.env[
            "automatic.workflow.job"
        ]._do_sale_done_job_options(sale, [])

        self.assertEqual(create_invoice_options["identity_key"], identity_exact)
        self.assertIn(sale.display_name, create_invoice_options["description"])

        self.assertEqual(validate_invoice_options["identity_key"], identity_exact)
        self.assertIn(invoice.display_name, validate_invoice_options["description"])

        self.assertEqual(sale_done_options["identity_key"], identity_exact)
        self.assertIn(sale.display_name, sale_done_options["description"])

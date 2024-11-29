# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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

    def assert_job_delayed(self, delayable_cls, delayable, method_name, args):
        # .with_delay() has been called once
        self.assertEqual(delayable_cls.call_count, 1)
        delay_args, delay_kwargs = delayable_cls.call_args
        # .with_delay() has been called on self.env["automatic.workflow.job"]
        self.assertEqual(delay_args, (self.env["automatic.workflow.job"],))
        # .with_delay() with the following options
        self.assertEqual(delay_kwargs.get("identity_key"), identity_exact)
        # check what's passed to the job method
        method = getattr(delayable, method_name)
        self.assertEqual(method.call_count, 1)
        delay_args, delay_kwargs = method.call_args
        self.assertEqual(delay_args, args)
        self.assertDictEqual(delay_kwargs, {})

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

# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.queue_job.job import Job, identity_exact
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

    def test_failed_job_not_enqueued_again(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        sale.action_confirm()
        sale._create_invoices()
        invoice = sale.invoice_ids
        domain = [
            ("state", "=", "draft"),
            ("posted_before", "=", False),
            ("workflow_process_id", "=", sale.workflow_process_id.id),
        ]
        job_model = self.env["automatic.workflow.job"]
        failed = Job(
            job_model._do_validate_invoice,
            args=(invoice, domain),
            identity_key=identity_exact,
        )
        failed.store()
        failed.db_record().write({"state": "failed"})
        with trap_jobs() as trap:
            self.run_job()
            trap.assert_jobs_count(0, only=job_model._do_validate_invoice)
        failed.db_record().write({"state": "cancelled"})
        with trap_jobs() as trap:
            self.run_job()
            trap.assert_jobs_count(1, only=job_model._do_validate_invoice)

    def test_failed_job_of_another_record_does_not_block(self):
        workflow = self.create_full_automatic()
        sale = self.create_sale_order(workflow)
        other = self.create_sale_order(workflow)
        job_model = self.env["automatic.workflow.job"]
        domain = [
            ("state", "=", "draft"),
            ("workflow_process_id", "=", workflow.id),
        ]
        failed = Job(
            job_model._do_validate_sale_order,
            args=(other, domain),
            identity_key=identity_exact,
        )
        failed.store()
        failed.db_record().write({"state": "failed"})
        with trap_jobs() as trap:
            self.run_job()
            trap.assert_jobs_count(1, only=job_model._do_validate_sale_order)
            trap.assert_enqueued_job(
                job_model._do_validate_sale_order,
                args=(sale, domain),
                kwargs={},
                properties={"identity_key": identity_exact},
            )

# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tools.safe_eval import safe_eval

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import mock_with_delay, trap_jobs
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
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)
        with mock_with_delay() as (delayable_cls, delayable):
            self.run_job()  # run automatic workflow cron
            args = (
                self.sale,
                [
                    ("state", "=", "draft"),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )
            self.assert_job_delayed(
                delayable_cls, delayable, "_do_validate_sale_order", args
            )

    def test_create_invoice(self):
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)
        self.sale.action_confirm()
        # don't care about transfers in this test
        self.sale.picking_ids.state = "done"
        with mock_with_delay() as (delayable_cls, delayable):
            self.run_job()  # run automatic workflow cron
            args = (
                self.sale,
                [
                    ("state", "in", ["sale", "done"]),
                    ("invoice_status", "=", "to invoice"),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )
            self.assert_job_delayed(
                delayable_cls, delayable, "_do_create_invoice", args
            )

    def test_validate_invoice(self):
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)
        self.sale.action_confirm()
        # don't care about transfers in this test
        self.sale.picking_ids.state = "done"
        self.sale._create_invoices()
        invoice = self.sale.invoice_ids
        with mock_with_delay() as (delayable_cls, delayable):
            self.run_job()  # run automatic workflow cron
            args = (
                invoice,
                [
                    ("state", "=", "draft"),
                    ("posted_before", "=", False),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )
            self.assert_job_delayed(
                delayable_cls, delayable, "_do_validate_invoice", args
            )

    def test_validate_picking(self):
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)
        self.sale.action_confirm()
        picking = self.sale.picking_ids
        # disable invoice creation in this test
        self.sale.workflow_process_id.create_invoice = False
        with mock_with_delay() as (delayable_cls, delayable):
            self.run_job()  # run automatic workflow cron
            args = (
                picking,
                [
                    ("state", "in", ["draft", "confirmed", "assigned"]),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )
            self.assert_job_delayed(
                delayable_cls, delayable, "_do_validate_picking", args
            )

    def test_sale_done(self):
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)
        self.sale.action_confirm()
        # don't care about transfers in this test
        self.sale.picking_ids.state = "done"
        self.sale._create_invoices()

        # disable invoice validation for we don't care
        # in this test
        self.sale.workflow_process_id.validate_invoice = False
        # activate the 'sale done' workflow
        self.sale.workflow_process_id.sale_done = True

        with mock_with_delay() as (delayable_cls, delayable):
            self.run_job()  # run automatic workflow cron
            args = (
                self.sale,
                [
                    ("state", "=", "sale"),
                    ("invoice_status", "=", "invoiced"),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )
            self.assert_job_delayed(delayable_cls, delayable, "_do_sale_done", args)

    def test_deleted_sale_order(self):
        workflow = self.create_full_automatic()
        workflow_domain = [("workflow_process_id", "=", workflow.id)]
        self.sale = self.create_sale_order(workflow)
        with trap_jobs() as trap:
            self.run_job()
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                self.env["automatic.workflow.job"]._do_validate_sale_order,
                args=(
                    self.sale,
                    safe_eval(workflow.order_filter_id.domain) + workflow_domain,
                ),
            )
            job = trap.enqueued_jobs[0]
            self.assertEqual(job.state, "pending")
            self.sale.unlink()
            trap.perform_enqueued_jobs()

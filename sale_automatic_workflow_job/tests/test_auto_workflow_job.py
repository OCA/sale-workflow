# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import mock_with_delay
from odoo.addons.sale_automatic_workflow.tests.test_automatic_workflow_base import (  # noqa
    TestAutomaticWorkflowBase,
)


@tagged("post_install", "-at_install")
class TestAutoWorkflowJob(TestAutomaticWorkflowBase):
    def setUp(self):
        super().setUp()
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)

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
        with mock_with_delay() as (delayable_cls, delayable):
            self.progress()  # run automatic workflow cron
            self.assert_job_delayed(
                delayable_cls, delayable, "_do_validate_sale_order", (self.sale,)
            )

    def test_create_invoice(self):
        self.sale.action_confirm()
        # don't care about transfers in this test
        self.sale.picking_ids.state = "done"
        with mock_with_delay() as (delayable_cls, delayable):
            self.progress()  # run automatic workflow cron
            self.assert_job_delayed(
                delayable_cls, delayable, "_do_create_invoice", (self.sale,)
            )

    def test_validate_invoice(self):
        self.sale.action_confirm()
        # don't care about transfers in this test
        self.sale.picking_ids.state = "done"
        self.sale.action_invoice_create()
        invoice = self.sale.invoice_ids
        with mock_with_delay() as (delayable_cls, delayable):
            self.progress()  # run automatic workflow cron
            self.assert_job_delayed(
                delayable_cls, delayable, "_do_validate_invoice", (invoice,)
            )

    def test_validate_picking(self):
        self.sale.action_confirm()
        picking = self.sale.picking_ids
        # disable invoice creation in this test
        self.sale.workflow_process_id.create_invoice = False
        with mock_with_delay() as (delayable_cls, delayable):
            self.progress()  # run automatic workflow cron
            self.assert_job_delayed(
                delayable_cls, delayable, "_do_validate_picking", (picking,)
            )

    def test_sale_done(self):
        self.sale.action_confirm()
        # don't care about transfers in this test
        self.sale.picking_ids.state = "done"
        self.sale.action_invoice_create()

        # disable invoice validation for we don't care
        # in this test
        self.sale.workflow_process_id.validate_invoice = False
        # activate the 'sale done' workflow
        self.sale.workflow_process_id.sale_done = True

        with mock_with_delay() as (delayable_cls, delayable):
            self.progress()  # run automatic workflow cron
            self.assert_job_delayed(
                delayable_cls, delayable, "_do_sale_done", (self.sale,)
            )

# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from freezegun import freeze_time

from odoo.tests import tagged

from odoo.addons.sale_automatic_workflow.tests.common import (
    TestAutomaticWorkflowMixin,
    TestCommon,
)


@tagged("post_install", "-at_install")
class TestAutoWorkflowPeriodicity(TestCommon, TestAutomaticWorkflowMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                # Compatibility with sale_automatic_workflow_job: even if
                # the module is installed, ensure we don't delay a job.
                # Thus, we test the usual flow.
                _job_force_sync=True,
            )
        )

    def test_delayed_execution_15_minutes(self):
        """Check sales are delayed processing."""
        workflow = self.create_full_automatic()
        # Execute every 15 minutes
        workflow.periodicity = 900
        workflow.next_execution = False
        self.sale1 = self.create_sale_order(workflow)
        # Fist execution at 12:00
        with freeze_time("2023-05-08 12:00:00"):
            self.env["automatic.workflow.job"].run()
        self.assertEqual(self.sale1.state, "sale")
        self.sale2 = self.create_sale_order(workflow)
        # 5 minutes later no execution should happen
        with freeze_time("2023-05-08 12:05:00"):
            self.env["automatic.workflow.job"].run()
        self.assertEqual(self.sale2.state, "draft")
        # 15 minutes after 12:00 it is executed
        with freeze_time("2023-05-08 12:15:09"):
            self.env["automatic.workflow.job"].run()
        self.assertEqual(self.sale2.state, "sale")

    def test_change_period_reset_next_exceution(self):
        """Check changing the period does reset the next execution."""
        workflow = self.create_full_automatic()
        # Execute every 15 minutes
        workflow.periodicity = 900
        workflow.next_execution = False
        self.sale1 = self.create_sale_order(workflow)
        with freeze_time("2023-05-08 12:00:00"):
            self.env["automatic.workflow.job"].run()
        self.assertEqual(self.sale1.state, "sale")
        self.assertTrue(workflow.next_execution)
        workflow.periodicity = 0
        self.assertFalse(workflow.next_execution)
        with freeze_time("2023-05-08 12:30:00"):
            workflow.periodicity = 900
        self.assertEqual(
            workflow.next_execution.strftime("%Y-%m-%d %H:%M:%S"), "2023-05-08 12:45:00"
        )

    def test_enforce_on_creation_time(self):
        workflow = self.create_full_automatic()
        # Execute every 15 minutes
        workflow.periodicity = 900
        workflow.next_execution = False
        workflow.periodicity_check_create_date = True
        self.sale1 = self.create_sale_order(workflow)
        create_date = self.sale1.create_date
        # Less than 15 minutes since the sale has been created
        run_date = create_date + timedelta(seconds=800)
        with freeze_time(run_date):
            self.env["automatic.workflow.job"].run()
        # It is not process by the job
        self.assertEqual(self.sale1.state, "draft")
        workflow.next_execution = False
        # More than 15 minutes
        run_date = create_date + timedelta(seconds=1000)
        with freeze_time(run_date):
            self.env["automatic.workflow.job"].run()
        # It is processed
        self.assertEqual(self.sale1.state, "sale")

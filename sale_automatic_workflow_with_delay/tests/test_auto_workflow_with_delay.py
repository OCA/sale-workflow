# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import tagged

from odoo.addons.sale_automatic_workflow.tests.common import (
    TestAutomaticWorkflowMixin,
    TestCommon,
)


@tagged("post_install", "-at_install")
class TestAutoWorkflowWithDelay(TestCommon, TestAutomaticWorkflowMixin):
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

    def test_not_validate_sale_order_with_delay(self):
        workflow = self.create_full_automatic()
        workflow.validate_order_with_delay = True
        self.sale = self.create_sale_order(workflow)
        self.env["automatic.workflow.job"].run()
        self.assertEqual(self.sale.state, "draft")
        # Standard flow validates fine.
        workflow.validate_order_with_delay = False
        self.env["automatic.workflow.job"].run()
        self.assertEqual(self.sale.state, "sale")

    def test_validate_sale_order_with_delay(self):
        workflow = self.create_full_automatic()
        workflow.validate_order_with_delay = True
        self.sale = self.create_sale_order(workflow)
        self.env["automatic.workflow.job"].run()
        self.assertEqual(self.sale.state, "draft")
        self.env["automatic.workflow.job"].run_with_delay()
        self.assertEqual(self.sale.state, "sale")

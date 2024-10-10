# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import tagged

from odoo.addons.sale_automatic_workflow.tests.common import (
    TestAutomaticWorkflowMixin,
    TestCommon,
)


@tagged("post_install", "-at_install")
class TestAutomaticWorkflow(TestCommon, TestAutomaticWorkflowMixin):
    def test_automatic_workflow_advance(self):
        workflow = self.create_full_automatic()
        workflow.automated_advance_payment_create = True
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.workflow_process_id, workflow)
        self.run_job()
        self.assertEqual(sale.state, "sale")
        self.assertEqual(sale.amount_total, sale.account_payment_ids.amount)

    def test_workflow_without_advance(self):
        workflow = self.create_full_automatic()
        workflow.automated_advance_payment_create = False
        sale = self.create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.workflow_process_id, workflow)
        self.run_job()
        self.assertEqual(sale.state, "sale")
        self.assertFalse(sale.account_payment_ids)
        self.assertEqual(sale.amount_residual, sale.amount_total)

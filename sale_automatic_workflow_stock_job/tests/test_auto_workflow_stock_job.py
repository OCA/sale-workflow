# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.sale_automatic_workflow.tests.common import TestCommon
from odoo.addons.sale_automatic_workflow_stock.tests.common import (
    TestAutomaticWorkflowStockMixin,
)


@tagged("post_install", "-at_install")
class TestAutoWorkflowJob(TestCommon, TestAutomaticWorkflowStockMixin):
    def test_validate_picking(self):
        workflow = self.create_full_automatic()
        self.sale = self.create_sale_order(workflow)
        self.sale.action_confirm()
        picking = self.sale.picking_ids
        # disable invoice creation in this test
        self.sale.workflow_process_id.create_invoice = False

        with trap_jobs() as trap:
            self.run_job()  # run automatic workflow cron

            trap.assert_jobs_count(
                1, only=self.env["automatic.workflow.job"]._do_validate_picking
            )

            args = (
                picking,
                [
                    ("state", "in", ["draft", "confirmed", "assigned"]),
                    ("workflow_process_id", "=", self.sale.workflow_process_id.id),
                ],
            )

            trap.assert_enqueued_job(
                self.env["automatic.workflow.job"]._do_validate_picking,
                args=args,
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )

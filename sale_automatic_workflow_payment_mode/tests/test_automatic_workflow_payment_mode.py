# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sale_automatic_workflow.tests.common import (
    TestAutomaticWorkflowMixin,
    TestCommon,
)


class TestAutomaticWorkflowPaymentMode(TestCommon, TestAutomaticWorkflowMixin):
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

    def create_sale_order(self, workflow, override=None):
        new_order = super().create_sale_order(workflow, override)
        return new_order

    def create_full_automatic(self, override=None):
        workflow = super().create_full_automatic(override)
        reg_pay_dict = {"register_payment": True}
        workflow.update(reg_pay_dict)

        self.pay_method = self.env["account.payment.method"].create(
            {"name": "default inbound", "code": "definb", "payment_type": "inbound"}
        )
        self.acc_journ = self.env["account.journal"].create(
            {"name": "Bank US", "type": "bank", "code": "BNK68"}
        )
        self.pay_mode = self.env["account.payment.mode"].create(
            {
                "name": "Julius Caesare payment",
                "bank_account_link": "fixed",
                "fixed_journal_id": self.acc_journ.id,
                "payment_method_id": self.pay_method.id,
                "workflow_process_id": workflow.id,
            }
        )
        return workflow

    def test_full_automatic(self):
        workflow = self.create_full_automatic()
        self.pay_mode.write(
            {
                "bank_account_link": "variable",
                "fixed_journal_id": False,
            }
        )
        sale = self.create_sale_order(workflow)

        sale.payment_mode_id = False
        sale.onchange_payment_mode_set_workflow()
        self.assertFalse(sale.workflow_process_id)
        sale.payment_mode_id = self.pay_mode
        sale._onchange_workflow_process_id()
        sale.onchange_payment_mode_set_workflow()

        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.workflow_process_id, workflow)
        self.env["automatic.workflow.job"].run()
        self.assertEqual(sale.state, "sale")
        self.assertTrue(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.payment_state, "not_paid")

        self.pay_mode.write(
            {
                "bank_account_link": "fixed",
                "fixed_journal_id": self.acc_journ,
            }
        )
        self.env["automatic.workflow.job"].run()
        self.assertEqual(invoice.payment_state, "paid")
        picking = sale.picking_ids
        self.assertEqual(picking.state, "done")

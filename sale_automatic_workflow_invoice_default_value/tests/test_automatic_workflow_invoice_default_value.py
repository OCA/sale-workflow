# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sale_automatic_workflow.tests.common import (
    TestAutomaticWorkflowMixin,
    TestCommon,
)


class TestAutomaticWorkflowInvoiceDefaultValues(TestCommon, TestAutomaticWorkflowMixin):
    def _get_override_workflow_values(self, with_default_values):
        if with_default_values:
            invoice_default_values = [
                {
                    "invoice_field_id": self.ref("account.field_account_move__name"),
                    "value_type": "default_char_value",
                    "default_char_value": "Test Default Move Name",
                },
                {
                    "invoice_field_id": self.ref("account.field_account_move__ref"),
                    "value_type": "from_sale_order",
                    "sale_order_field_id": self.ref("sale.field_sale_order__reference"),
                },
            ]
        else:
            invoice_default_values = []

        workflow_values = {
            "validate_invoice": False,
            "create_invoice_default_value_ids": [
                (0, 0, values) for values in invoice_default_values
            ],
        }
        return workflow_values

    def _test_common_and_return_invoice(self, with_default_values):
        workflow_override = self._get_override_workflow_values(
            with_default_values=with_default_values
        )
        workflow = self.create_full_automatic(workflow_override)
        sale_override = {"reference": "Test - ref"}
        sale = self.create_sale_order(workflow, sale_override)

        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.workflow_process_id, workflow)

        with self.cr.savepoint():  # To avoid cache problems
            self.run_job()

        self.assertEqual(sale.state, "sale")
        self.assertTrue(sale.invoice_ids)

        return sale.invoice_ids

    def test_automatic_with_invoice_default_values(self):
        invoice = self._test_common_and_return_invoice(with_default_values=True)

        self.assertEqual(invoice.name, "Test Default Move Name")
        self.assertEqual(invoice.ref, "Test - ref")

    def test_automatic_without_invoice_default_values(self):
        invoice = self._test_common_and_return_invoice(with_default_values=False)

        self.assertEqual(invoice.name, "/")
        self.assertFalse(invoice.ref)

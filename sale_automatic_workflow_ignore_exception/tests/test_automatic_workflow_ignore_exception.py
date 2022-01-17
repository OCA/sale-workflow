# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sale_automatic_workflow.tests.common import (
    TestAutomaticWorkflowMixin,
    TestCommon,
)


class TestAutomaticWorkflowIgnoreException(TestCommon, TestAutomaticWorkflowMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        exception = cls.env.ref("sale_exception.excep_no_zip").sudo()
        exception.active = True

    def _get_override_workflow_values(self, ignore_exception):
        return {
            "validate_picking": False,
            "create_invoice": False,
            "validate_invoice": False,
            "ignore_exception_when_confirm": ignore_exception,
        }

    def _test_common_and_return_sale(self, ignore_exception):
        workflow_override = self._get_override_workflow_values(
            ignore_exception=ignore_exception
        )
        workflow = self.create_full_automatic(workflow_override)
        sale = self.create_sale_order(workflow)

        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.ignore_exception, False)
        self.assertEqual(sale.workflow_process_id, workflow)

        with self.cr.savepoint():  # To avoid cache problems
            self.run_job()

        return sale

    def test_automatic_with_ignore_exception(self):
        sale = self._test_common_and_return_sale(ignore_exception=True)

        self.assertEqual(sale.state, "sale")
        self.assertEqual(sale.ignore_exception, True)

    def test_automatic_without_ignore_exception(self):
        sale = self._test_common_and_return_sale(ignore_exception=False)

        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.ignore_exception, False)

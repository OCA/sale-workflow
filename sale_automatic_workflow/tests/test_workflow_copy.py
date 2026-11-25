# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCommon


class TestWorkflowCopy(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.workflow = cls.env["sale.workflow.process"].create(
            {"name": "Manual workflow"}
        )
        partner = cls.env["res.partner"].create({"name": "Test Partner"})
        product = cls.env["product.product"].create(
            {"name": "Test Product", "list_price": 5.0, "type": "consu"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "workflow_process_id": cls.workflow.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "price_unit": product.list_price,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

    def _set_mode(self, mode):
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_automatic_workflow.sale_workflow_copy_mode", mode
        )

    def test_no_copy_is_default(self):
        # ``workflow_process_id`` has ``copy=False``; without the setting the copy is
        # created without a workflow.
        new_order = self.order.copy()
        self.assertFalse(new_order.workflow_process_id)

    def test_copy_propagates_workflow(self):
        self._set_mode("copy")
        new_order = self.order.copy()
        self.assertEqual(new_order.workflow_process_id, self.workflow)

    def test_explicit_default_wins_over_setting(self):
        # A workflow forced through ``default`` must not be overridden by the setting.
        self._set_mode("copy")
        other = self.env["sale.workflow.process"].create({"name": "Other"})
        new_order = self.order.copy({"workflow_process_id": other.id})
        self.assertEqual(new_order.workflow_process_id, other)

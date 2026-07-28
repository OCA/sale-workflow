# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWorkflowAutoAssign(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env["sale.workflow.process"].search([]).write({"auto_assign": False})
        cls.workflow = cls.env["sale.workflow.process"].create(
            {"name": "Auto Assign Workflow", "auto_assign": True}
        )

    def _create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_12").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Product 1",
                            "product_id": self.env.ref("product.product_product_5").id,
                            "product_uom_qty": 2,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

    def test_auto_assign_ok(self):
        """Check workflow is assigned to sale."""
        self.workflow.auto_assign = True
        self.workflow.auto_assign_domain = "[('partner_id.name', 'ilike', 'Azure%')]"
        sale = self._create_sale_order()
        self.assertEqual(sale.workflow_process_id, self.workflow)

    def test_auto_assign_disabled(self):
        """Check workflow is not assigned because auto assign is disabled."""
        self.workflow.auto_assign = False
        self.workflow.auto_assign_domain = "[('partner_id.name', 'ilike', 'Azure%')]"
        sale = self._create_sale_order()
        self.assertFalse(sale.workflow_process_id)

    def test_auto_assign_not_ok(self):
        """Check workflow is not assigned because it does not apply."""
        self.workflow.auto_assign = True
        self.workflow.auto_assign_domain = "[('partner_id.name', 'ilike', 'Hello%')]"
        sale = self._create_sale_order()
        self.assertFalse(sale.workflow_process_id)

    def test_auto_assign_priority(self):
        """Check the lowest priority value wins among matching workflows."""
        # Isolate: only the workflows created here should match the order.
        self.workflow.auto_assign = False
        domain = "[('partner_id.name', 'ilike', 'Azure%')]"
        low = self.env["sale.workflow.process"].create(
            {
                "name": "Low Priority Workflow",
                "auto_assign": True,
                "auto_assign_domain": domain,
                "auto_assign_priority": 30,
            }
        )
        # Only candidate so far: it gets assigned.
        self.assertEqual(self._create_sale_order().workflow_process_id, low)
        # A copy with a lower priority value takes precedence.
        high = low.copy({"name": "High Priority Workflow", "auto_assign_priority": 10})
        self.assertEqual(self._create_sale_order().workflow_process_id, high)
        # A third, mid-priority workflow does not steal the win from high.
        low.copy({"name": "Mid Priority Workflow", "auto_assign_priority": 20})
        self.assertEqual(self._create_sale_order().workflow_process_id, high)

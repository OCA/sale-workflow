# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.payment.tests.common import PaymentCommon


class TestActionPaid(PaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product",
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create({"product_id": cls.product.id, "product_uom_qty": 1})
                ],
            }
        )

    def test_action_paid(self):
        """Test that the communication displayed is the sale order reference."""
        self.sale_order.state = "sent"
        tx = self._create_transaction(
            flow="direct", state="pending", sale_order_ids=[self.sale_order.id]
        )
        self.assertEqual(tx.state, "pending")
        self.env["ir.config_parameter"].sudo().set_param(
            "sale.automatic_invoice", "True"
        )
        self.product.invoice_policy = "delivery"
        self.sale_order.action_paid()
        self.assertEqual(tx.state, "done")
        self.assertEqual(self.sale_order.state, "sale")
        # Check the policy changed to "order" and the invoice is generated
        self.assertTrue(tx.invoice_ids)
        self.assertEqual(tx.invoice_ids[0].state, "posted")

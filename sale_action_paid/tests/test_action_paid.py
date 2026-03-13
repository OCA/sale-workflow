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
                "invoice_policy": "delivery",
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
        cls.sale_order.state = "sent"

    def test_action_paid_webshop_order(self):
        """Mark a sent SO with a pending transaction as paid"""
        tx = self._create_transaction(
            flow="direct", state="pending", sale_order_ids=[self.sale_order.id]
        )
        self.assertEqual(tx.state, "pending")
        self.env["ir.config_parameter"].sudo().set_param(
            "sale.automatic_invoice", "True"
        )
        self.sale_order.action_paid()
        self.assertEqual(tx.state, "done")
        self.assertEqual(self.sale_order.state, "sale")
        # Check the policy changed to "order" and the invoice is generated
        self.assertEqual(len(tx.invoice_ids), 1)
        self.assertEqual(tx.invoice_ids.state, "posted")

    def test_action_paid_manual_order(self):
        """Mark a manual SO without a pending transaction as paid"""
        tx = self.sale_order.transaction_ids
        self.assertFalse(tx)
        tx = self.sale_order._action_paid_create_transaction(
            payment_method_id=self.payment_method_id
        )
        self.sale_order._action_paid(tx, auto_invoice=True)
        self.assertEqual(len(tx), 1)
        self.assertEqual(tx.state, "done")
        self.assertEqual(self.sale_order.state, "sale")
        # Check the policy changed to "order" and the invoice is generated
        self.assertEqual(len(tx.invoice_ids), 1)
        self.assertEqual(tx.invoice_ids.state, "posted")

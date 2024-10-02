# Copyright 2024 Binhex - Zuzanna Elzbieta Szalaty Szalaty.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_id = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_id.id,
            }
        )
        cls.provider = cls.env["payment.provider"].create(
            {
                "name": "Test",
                "code": "none",
            }
        )

    def test_compute_payment_transaction_count(self):
        self.assertEqual(self.sale_order.payment_transaction_count, 0)
        transaction1 = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 100,
                "currency_id": self.env.company.currency_id.id,
            }
        )
        transaction2 = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 200,
                "currency_id": self.env.company.currency_id.id,
            }
        )
        self.sale_order.transaction_ids = [transaction1.id, transaction2.id]
        self.assertEqual(self.sale_order.payment_transaction_count, 2)
        transaction1.unlink()
        self.assertEqual(self.sale_order.payment_transaction_count, 1)

    def test_action_view_transaction(self):
        action = self.sale_order.action_view_transaction()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Payment Transactions")
        self.assertEqual(action["res_model"], "payment.transaction")
        self.assertEqual(action["view_mode"], "tree,form")
        self.assertEqual(action["domain"], [("id", "in", [])])

        transaction = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 100,
                "currency_id": self.env.company.currency_id.id,
            }
        )
        self.sale_order.transaction_ids = [transaction.id]
        action = self.sale_order.action_view_transaction()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Payment Transactions")
        self.assertEqual(action["res_model"], "payment.transaction")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["res_id"], transaction.id)

        transaction1 = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 100,
                "currency_id": self.env.company.currency_id.id,
            }
        )
        transaction2 = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "partner_id": self.partner_id.id,
                "amount": 200,
                "currency_id": self.env.company.currency_id.id,
            }
        )
        self.sale_order.transaction_ids = [transaction1.id, transaction2.id]
        action = self.sale_order.action_view_transaction()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Payment Transactions")
        self.assertEqual(action["res_model"], "payment.transaction")
        self.assertEqual(action["view_mode"], "tree,form")
        self.assertEqual(
            action["domain"], [("id", "in", [transaction1.id, transaction2.id])]
        )

# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestSaleOrderCancelExistingInvoice(TransactionCase):
    def setUp(self):
        super(TestSaleOrderCancelExistingInvoice, self).setUp()

        self.product = self.env.ref("product.product_product_4")
        self.partner = self.env.ref("base.res_partner_1")
        self.advance_obj = self.env["sale.advance.payment.inv"]

    def _create_sale(self):
        line = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "product_uom": self.product.uom_id.id,
                    "product_uom_qty": 3.0,
                },
            )
        ]
        vals = {
            "partner_id": self.partner.id,
            "order_line": line,
        }
        self.sale = self.env["sale.order"].create(vals)

    def _create_invoice_advance(self):
        vals = {
            "advance_payment_method": "percentage",
            "amount": 10.0,
        }
        self.advance = self.advance_obj.create(vals)

    def test_cancel_refused(self):
        self._create_sale()
        self._create_invoice_advance()

        self.advance.with_context(active_ids=[self.sale.id]).create_invoices()
        self.sale.invoice_ids.action_post()

        with self.assertRaises(UserError):
            self.sale.action_cancel()

    def test_cancel_invoice_reversed(self):
        self._create_sale()
        self._create_invoice_advance()

        self.advance.with_context(active_ids=[self.sale.id]).create_invoices()
        invoice_id = self.sale.invoice_ids
        invoice_id.action_post()

        ctx = {
            "active_model": invoice_id._name,
            "active_ids": invoice_id.ids,
            "active_id": invoice_id.id,
        }
        wizard_obj = self.env["account.move.reversal"].with_context(**ctx)
        wizard = wizard_obj.create(
            {
                "refund_method": "cancel",
                "reason": "reason test create",
            }
        )
        wizard.reverse_moves()
        self.assertEqual(invoice_id.payment_state, "reversed")
        self.sale.action_cancel()
        self.assertEqual(self.sale.state, "cancel")

    def test_cancel_invoice_paid(self):
        journal_id = self.env["account.journal"].create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BNK67",
            }
        )
        self._create_sale()
        self._create_invoice_advance()

        self.advance.with_context(active_ids=[self.sale.id]).create_invoices()
        invoice_id = self.sale.invoice_ids
        invoice_id.action_post()

        ctx = {
            "active_model": invoice_id._name,
            "active_ids": invoice_id.ids,
            "active_id": invoice_id.id,
        }
        wizard_obj = self.env["account.payment.register"].with_context(**ctx)
        wizard = wizard_obj.create(
            {
                "amount": invoice_id.amount_total,
                "journal_id": journal_id.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        wizard._create_payments()

        self.assertEqual(invoice_id.payment_state, "paid")
        self.sale.action_cancel()
        self.assertEqual(self.sale.state, "cancel")

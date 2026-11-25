# Copyright 2026 OBS Solutions B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestSaleOrderPaymentState(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref("sales_team.group_sale_manager")
        cls.product_a.invoice_policy = "order"
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_a.id,
                            "product_uom_qty": 2.0,
                            "price_unit": 500.0,
                            "tax_ids": [Command.clear()],
                        }
                    )
                ],
            }
        )
        cls.order.action_confirm()

    def _invoice(self, post=True):
        invoice = self.order._create_invoices()
        if post:
            invoice.action_post()
        return invoice

    def _pay(self, invoice, amount):
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create({"amount": amount})._create_payments()

    def _search(self, filter_domain):
        return self.env["sale.order"].search(
            [("id", "=", self.order.id), *filter_domain]
        )

    def test_no_invoice(self):
        self.assertEqual(self.order.invoice_payment_state, "no_invoice")
        self.assertEqual(self.order.invoice_amount_residual, 0.0)

    def test_draft_invoice_ignored(self):
        self._invoice(post=False)
        self.assertEqual(self.order.invoice_payment_state, "no_invoice")
        self.assertEqual(self.order.invoice_amount_residual, 0.0)

    def test_posted_invoice_not_paid(self):
        self._invoice()
        self.assertEqual(self.order.invoice_payment_state, "not_paid")
        self.assertEqual(self.order.invoice_amount_residual, 1000.0)

    def test_partial_payment(self):
        invoice = self._invoice()
        self._pay(invoice, 400.0)
        self.assertEqual(self.order.invoice_payment_state, "partial")
        self.assertEqual(self.order.invoice_amount_residual, 600.0)

    def test_full_payment(self):
        invoice = self._invoice()
        self._pay(invoice, 1000.0)
        self.assertEqual(self.order.invoice_payment_state, invoice.payment_state)
        self.assertIn(self.order.invoice_payment_state, ("in_payment", "paid"))
        self.assertEqual(self.order.invoice_amount_residual, 0.0)

    def test_partially_invoiced_but_paid(self):
        """Paid status only covers what is invoiced, not the whole order."""
        self.product_a.invoice_policy = "delivery"
        self.order.order_line.qty_delivered = 1.0
        invoice = self._invoice()
        self.assertEqual(invoice.amount_total, 500.0)
        self._pay(invoice, 500.0)
        self.order.order_line.qty_delivered = 2.0
        self.assertEqual(self.order.invoice_status, "to invoice")
        self.assertIn(self.order.invoice_payment_state, ("in_payment", "paid"))
        self.assertEqual(self.order.invoice_amount_residual, 0.0)

    def test_fully_reversed_invoice_ignored(self):
        invoice = self._invoice()
        reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"journal_id": invoice.journal_id.id})
        )
        reversal.refund_moves()
        refund = invoice.reversal_move_ids
        refund.action_post()
        self.assertEqual(invoice.payment_state, "reversed")
        self.assertEqual(self.order.invoice_payment_state, "no_invoice")
        self.assertEqual(self.order.invoice_amount_residual, 0.0)

    def test_partial_credit_note_deducted(self):
        invoice = self._invoice()
        refund = invoice._reverse_moves()
        refund.invoice_line_ids.write({"quantity": 1.0, "price_unit": 100.0})
        refund.action_post()
        # The credit note is reconciled with the invoice it reverses.
        self.assertEqual(self.order.invoice_amount_residual, 900.0)
        self.assertEqual(self.order.invoice_payment_state, "partial")

    def test_foreign_currency_invoice(self):
        other_currency = self.setup_other_currency("EUR")
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "currency_id": other_currency.id,
                "invoice_date": fields.Date.to_date("2017-01-01"),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "quantity": 1.0,
                            "price_unit": 200.0,
                            "tax_ids": [Command.clear()],
                            "sale_line_ids": [Command.set(self.order.order_line.ids)],
                        }
                    )
                ],
            }
        )
        invoice.action_post()
        # 200.0 EUR at a rate of 2.0 is 100.0 in the order currency.
        self.assertEqual(self.order.invoice_amount_residual, 100.0)
        self.assertEqual(self.order.invoice_payment_state, "not_paid")

    def test_get_invoice_payment_state(self):
        get_state = self.env["sale.order"]._get_invoice_payment_state
        self.assertEqual(get_state(set()), "no_invoice")
        self.assertEqual(get_state({"paid"}), "paid")
        self.assertEqual(get_state({"paid", "invoicing_legacy"}), "paid")
        self.assertEqual(get_state({"paid", "in_payment"}), "in_payment")
        self.assertEqual(get_state({"not_paid"}), "not_paid")
        self.assertEqual(get_state({"not_paid", "blocked"}), "not_paid")
        self.assertEqual(get_state({"partial"}), "partial")
        self.assertEqual(get_state({"paid", "not_paid"}), "partial")

    def test_filter_invoiced_and_paid(self):
        domain = [
            ("invoice_status", "=", "invoiced"),
            ("invoice_payment_state", "=", "paid"),
            "!",
            ("order_line.invoice_lines.parent_state", "=", "draft"),
        ]
        invoice = self._invoice()
        invoice.payment_state = "paid"
        self.assertEqual(self.order.invoice_payment_state, "paid")
        self.assertEqual(self._search(domain), self.order)
        # A new draft invoice means the order is not closed yet.
        self.order.order_line.product_uom_qty = 3.0
        self._invoice(post=False)
        self.assertFalse(self._search(domain))

    def test_filter_invoiced_unpaid(self):
        domain = [("invoice_payment_state", "in", ("not_paid", "partial"))]
        self.assertFalse(self._search(domain))
        self._invoice()
        self.assertEqual(self._search(domain), self.order)

    def test_amount_due_restricted_to_accounting(self):
        salesman = self.env["res.users"].create(
            {
                "name": "Salesman",
                "login": "sale_order_payment_state_salesman",
                "group_ids": [
                    Command.set([self.env.ref("sales_team.group_sale_salesman").id])
                ],
            }
        )
        fields_info = (
            self.env["sale.order"]
            .with_user(salesman)
            .fields_get(["invoice_payment_state", "invoice_amount_residual"])
        )
        self.assertIn("invoice_payment_state", fields_info)
        self.assertNotIn("invoice_amount_residual", fields_info)

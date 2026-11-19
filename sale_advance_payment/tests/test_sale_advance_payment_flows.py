# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestSaleAdvancePaymentFlows(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref("sales_team.group_sale_manager")
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.outstanding_account = cls.env["account.account"].create(
            {
                "name": "Outstanding Receipts Advance",
                "code": "101999",
                "account_type": "asset_current",
                "reconcile": True,
            }
        )
        cls.manual_in_line = cls.bank_journal.inbound_payment_method_line_ids[:1]
        cls.manual_in_line.payment_account_id = cls.outstanding_account
        cls.product = cls.env["product.product"].create(
            {
                "name": "Advance service",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 100.0,
                "taxes_id": False,
            }
        )

    def _create_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                            "tax_ids": False,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        return order

    def _wizard(self, order, **vals):
        values = {
            "journal_id": self.bank_journal.id,
            "amount_advance": 50.0,
            "order_id": order.id,
        }
        values.update(vals)
        return (
            self.env["account.voucher.wizard"]
            .with_context(
                active_id=order.id, active_ids=order.ids, active_model="sale.order"
            )
            .create(values)
        )

    def _advance(self, order, **vals):
        self._wizard(order, **vals).make_advance_payment()
        return order.account_payment_ids[-1:]

    def test_wizard_skips_method_without_outstanding_account(self):
        no_account_line = self.env["account.payment.method.line"].create(
            {
                "name": "No outstanding account",
                "journal_id": self.bank_journal.id,
                "payment_method_id": self.manual_in_line.payment_method_id.id,
            }
        )
        self.partner_a.property_inbound_payment_method_line_id = no_account_line
        order = self._create_order()
        with patch.object(
            type(self.env["account.move"]),
            "_get_invoice_in_payment_state",
            return_value="in_payment",
        ):
            wizard = self._wizard(order)
            self.assertNotIn(no_account_line, wizard.available_payment_method_line_ids)
            self.assertEqual(wizard.payment_method_line_id, self.manual_in_line)
            wizard.make_advance_payment()
        payment = order.account_payment_ids
        self.assertTrue(payment.move_id)
        self.assertEqual(payment.payment_method_line_id, self.manual_in_line)
        self.assertEqual(order.advance_payment_status, "partial")

    def test_wizard_uses_partner_preferred_method(self):
        preferred = self.env["account.payment.method.line"].create(
            {
                "name": "Preferred with account",
                "journal_id": self.bank_journal.id,
                "payment_method_id": self.manual_in_line.payment_method_id.id,
                "payment_account_id": self.outstanding_account.id,
            }
        )
        self.partner_a.property_inbound_payment_method_line_id = preferred
        order = self._create_order()
        self.assertEqual(self._wizard(order).payment_method_line_id, preferred)

    def test_wizard_outbound_uses_outbound_method(self):
        order = self._create_order()
        self._advance(order)
        wizard = self._wizard(order, payment_type="outbound", amount_advance=20.0)
        self.assertEqual(wizard.payment_method_line_id.payment_type, "outbound")
        wizard.make_advance_payment()
        refund = order.account_payment_ids.filtered(
            lambda p: p.payment_type == "outbound"
        )
        self.assertEqual(refund.payment_method_line_id.payment_type, "outbound")

    def _reconciled_payment_moves(self, invoice):
        term_lines = invoice.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        )
        return term_lines.matched_credit_ids.credit_move_id.move_id

    def _create_two_invoices(self):
        order_1, order_2 = self._create_order(), self._create_order()
        pay_1, pay_2 = self._advance(order_1), self._advance(order_2)
        return (
            (order_1._create_invoices(), pay_1),
            (order_2._create_invoices(), pay_2),
        )

    def _assert_own_advance(self, invoice, payment):
        self.assertEqual(self._reconciled_payment_moves(invoice), payment.move_id)
        self.assertAlmostEqual(invoice.amount_residual, 50.0)

    def test_batch_post_from_list_reconciles_own_advance(self):
        (inv_1, pay_1), (inv_2, pay_2) = self._create_two_invoices()
        self.env["validate.account.move"].with_context(
            active_model="account.move", active_ids=(inv_1 | inv_2).ids
        ).create({}).validate_move()
        self._assert_own_advance(inv_1, pay_1)
        self._assert_own_advance(inv_2, pay_2)

    def test_action_post_on_several_invoices(self):
        (inv_1, pay_1), (inv_2, pay_2) = self._create_two_invoices()
        (inv_1 | inv_2).action_post()
        self._assert_own_advance(inv_1, pay_1)
        self._assert_own_advance(inv_2, pay_2)

    def test_grouped_invoice_reconciles_all_advances(self):
        order_1, order_2 = self._create_order(), self._create_order()
        pay_1, pay_2 = self._advance(order_1), self._advance(order_2)
        invoice = (order_1 | order_2)._create_invoices()
        self.assertEqual(len(invoice), 1)
        invoice.action_post()
        self.assertEqual(
            self._reconciled_payment_moves(invoice), pay_1.move_id | pay_2.move_id
        )
        self.assertAlmostEqual(invoice.amount_residual, 100.0)

    def test_advance_bigger_than_invoice(self):
        order = self._create_order()
        payment = self._advance(order)
        invoice = order._create_invoices()
        invoice.invoice_line_ids.price_unit = 40.0
        invoice.action_post()
        self.assertTrue(invoice.currency_id.is_zero(invoice.amount_residual))
        payment_line = payment.move_id.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        self.assertAlmostEqual(payment_line.amount_residual, -10.0)

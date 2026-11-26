# Copyright 2026 Studio73
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields

from odoo.addons.base.tests.common import BaseCommon


class TestGroupedInvoicePayment(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Grouped invoice customer"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Grouped invoice service", "invoice_policy": "order"}
        )
        cls.bank = cls.env["account.journal"].create(
            {"name": "Grouped payment bank", "type": "bank", "code": "GPB"}
        )

    def _make_order(self, amounts):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": amount,
                            "tax_id": [Command.clear()],
                        }
                    )
                    for amount in amounts
                ],
            }
        )
        order.action_confirm()
        return order

    def _make_invoice(self, lines, move_type="out_invoice", currency=None):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": move_type,
                "currency_id": (currency or self.env.company.currency_id).id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": "Invoice line",
                            "quantity": 1,
                            "price_unit": amount,
                            "tax_ids": [Command.clear()],
                            "sale_line_ids": [Command.set(sale_lines.ids)],
                        }
                    )
                    for amount, sale_lines in lines
                ],
            }
        )
        invoice.action_post()
        return invoice

    def _pay(self, invoice, amount):
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create(
            {
                "amount": amount,
                "journal_id": self.bank.id,
                "payment_difference_handling": "open",
            }
        )._create_payments()

    def _advance(self, order, amount):
        self.env["account.voucher.wizard"].with_context(
            active_id=order.id, active_ids=order.ids
        ).create(
            {
                "order_id": order.id,
                "journal_id": self.bank.id,
                "amount_advance": amount,
                "payment_type": "inbound",
            }
        ).make_advance_payment()

    def test_crossed_invoices_partial_and_complete(self):
        first = self._make_order([60, 40])
        second = self._make_order([40, 60])
        third = self._make_order([60, 40])
        a = self._make_invoice([(60, first.order_line[0]), (40, second.order_line[0])])
        b = self._make_invoice([(40, first.order_line[1]), (60, third.order_line[0])])
        c = self._make_invoice([(60, second.order_line[1]), (40, third.order_line[1])])
        self._pay(a, 50)
        self.assertEqual(
            (first.amount_residual, second.amount_residual, third.amount_residual),
            (70, 80, 100),
        )
        self._pay(b, 100)
        self.assertEqual(
            (first.amount_residual, second.amount_residual, third.amount_residual),
            (30, 80, 40),
        )
        self._pay(a, 50)
        self._pay(c, 100)
        self.assertEqual(
            (first.amount_residual, second.amount_residual, third.amount_residual),
            (0, 0, 0),
        )

    def test_unlinked_and_shared_lines(self):
        first = self._make_order([80])
        second = self._make_order([20])
        invoice = self._make_invoice(
            [
                (100, first.order_line | second.order_line),
                (20, self.env["sale.order.line"]),
            ]
        )
        self._pay(invoice, 120)
        self.assertEqual((first.amount_residual, second.amount_residual), (0, 0))

    def test_rounding_preserves_paid_cent(self):
        orders = self._make_order([1]) | self._make_order([1]) | self._make_order([1])
        invoice = self._make_invoice([(1, order.order_line) for order in orders])
        self._pay(invoice, 0.01)
        self.assertEqual(sorted(orders.mapped("amount_residual")), [0.99, 1, 1])
        before = orders.mapped("amount_residual")
        self._pay(invoice, 0.01)
        self.assertEqual(sorted(orders.mapped("amount_residual")), [0.99, 0.99, 1])
        for previous, order in zip(before, orders, strict=True):
            self.assertLessEqual(order.amount_residual, previous)

    def test_zero_total_invoice(self):
        order = self._make_order([100])
        invoice = self._make_invoice([(0, order.order_line)])
        self.assertEqual(invoice.amount_total, 0)
        self.assertEqual(order.amount_residual, 100)

    def test_zero_weights_split_equally(self):
        first = self._make_order([0])
        second = self._make_order([0])
        invoice = self._make_invoice([(10, first.order_line | second.order_line)])
        self._pay(invoice, 10)
        self.assertEqual((first.amount_residual, second.amount_residual), (-5, -5))

    def test_advance_belongs_to_its_order_on_grouped_invoice(self):
        first = self._make_order([60])
        second = self._make_order([40])
        self._advance(first, 30)
        self.assertEqual((first.amount_residual, second.amount_residual), (30, 40))
        invoice = self._make_invoice([(60, first.order_line), (40, second.order_line)])
        self.assertEqual(invoice.amount_residual, 70)
        self.assertEqual((first.amount_residual, second.amount_residual), (30, 40))
        self._pay(invoice, 35)
        self.assertEqual((first.amount_residual, second.amount_residual), (15, 20))
        self._pay(invoice, 35)
        self.assertEqual((first.amount_residual, second.amount_residual), (0, 0))

    def test_advance_from_each_order_on_grouped_invoice(self):
        first = self._make_order([60])
        second = self._make_order([40])
        self._advance(first, 60)
        self._advance(second, 10)
        invoice = self._make_invoice([(60, first.order_line), (40, second.order_line)])
        self.assertEqual(invoice.amount_residual, 30)
        self.assertEqual((first.amount_residual, second.amount_residual), (0, 30))
        self._pay(invoice, 30)
        self.assertEqual((first.amount_residual, second.amount_residual), (0, 0))

    def test_grouped_credit_note_is_allocated_to_each_order(self):
        first = self._make_order([60])
        second = self._make_order([40])
        invoice = self._make_invoice([(60, first.order_line), (40, second.order_line)])
        self._pay(invoice, 100)
        refund = self._make_invoice(
            [(30, first.order_line), (20, second.order_line)], "out_refund"
        )
        self._pay(refund, 50)
        self.assertEqual((first.amount_residual, second.amount_residual), (30, 20))

    def test_advance_exceeding_first_invoice_then_second_invoice(self):
        first = self._make_order([60, 40])
        second = self._make_order([40])
        self._advance(first, 80)
        invoice = self._make_invoice(
            [(60, first.order_line[0]), (40, second.order_line)]
        )
        self.assertEqual(invoice.amount_residual, 20)
        self.assertEqual((first.amount_residual, second.amount_residual), (20, 40))
        self._pay(invoice, 20)
        next_invoice = self._make_invoice([(40, first.order_line[1])])
        self.assertEqual(next_invoice.amount_residual, 40)
        self.assertEqual((first.amount_residual, second.amount_residual), (20, 20))

    def test_unreconcile_recomputes_both_orders(self):
        first = self._make_order([60])
        second = self._make_order([40])
        invoice = self._make_invoice([(60, first.order_line), (40, second.order_line)])
        self._pay(invoice, 50)
        self.assertEqual((first.amount_residual, second.amount_residual), (30, 20))
        invoice.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        ).remove_move_reconcile()
        self.assertEqual(invoice.amount_residual, 100)
        self.assertEqual((first.amount_residual, second.amount_residual), (60, 40))

    def test_grouped_invoice_with_negative_sale_line(self):
        first = self._make_order([60])
        second = self._make_order([10])
        invoice = self._make_invoice([(60, first.order_line), (-10, second.order_line)])
        self._pay(invoice, 50)
        self.assertEqual((first.amount_residual, second.amount_residual), (0, 20))

    def test_grouped_invoice_with_tax(self):
        tax = self.env["account.tax"].create(
            {"name": "Grouped invoice tax", "type_tax_use": "sale", "amount": 20}
        )
        first = self._make_order([60])
        second = self._make_order([40])
        (first.order_line | second.order_line).tax_id = [Command.set(tax.ids)]
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Taxable invoice line",
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": amount,
                            "tax_ids": [Command.set(tax.ids)],
                            "sale_line_ids": [Command.set(order.order_line.ids)],
                        }
                    )
                    for amount, order in [(60, first), (40, second)]
                ],
            }
        )
        invoice.action_post()
        self._pay(invoice, 60)
        self.assertEqual(invoice.amount_total, 120)
        self.assertEqual((first.amount_residual, second.amount_residual), (36, 24))
        self._pay(invoice, 60)
        self.assertEqual((first.amount_residual, second.amount_residual), (0, 0))

    def test_grouped_invoice_in_foreign_currency(self):
        first = self._make_order([60])
        second = self._make_order([40])
        currency = self.env.ref("base.EUR")
        currency.active = True
        invoice = self._make_invoice(
            [(60, first.order_line), (40, second.order_line)], currency=currency
        )
        self._pay(invoice, invoice.amount_residual)
        self.assertEqual(invoice.amount_residual, 0)
        expected_first = currency._convert(
            60, first.currency_id, first.company_id, invoice.invoice_date
        )
        expected_second = currency._convert(
            40, second.currency_id, second.company_id, invoice.invoice_date
        )
        self.assertAlmostEqual(first.amount_residual, 60 - expected_first, places=2)
        self.assertAlmostEqual(second.amount_residual, 40 - expected_second, places=2)

    def test_portal_does_not_request_paid_quotation(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "require_payment": True,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                            "tax_id": [Command.clear()],
                        }
                    )
                ],
            }
        )
        self.assertTrue(order._has_to_be_paid())
        self._advance(order, 100)
        self.assertFalse(order._has_to_be_paid())

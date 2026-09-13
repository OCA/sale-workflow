# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestSaleInvoicePartialWithDownPayment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "consu",
                "invoice_policy": "delivery",
                "list_price": 10.0,
            }
        )

    def _make_order(self, qty=100, price=10.0):
        f = Form(self.env["sale.order"])
        f.partner_id = self.partner
        with f.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = qty
            line.price_unit = price
        order = f.save()
        order.action_confirm()
        return order

    def _post_dp(self, order, pct=100.0):
        wiz = self.env["sale.advance.payment.inv"].create(
            {
                "sale_order_ids": [(6, 0, order.ids)],
                "advance_payment_method": "percentage",
                "amount": pct,
            }
        )
        wiz.create_invoices()
        inv = order.invoice_ids.filtered(lambda i: i.state == "draft")
        inv.action_post()
        return inv

    def _deliver(self, order, qty):
        picking = order.picking_ids.filtered(
            lambda p: p.state not in ("done", "cancel")
        )
        for move in picking.move_ids:
            move.quantity = qty
        if qty < sum(picking.move_ids.mapped("product_uom_qty")):
            backorder_wiz = picking.button_validate()
            backorder_wiz = Form(
                self.env[backorder_wiz["res_model"]].with_context(
                    **backorder_wiz["context"]
                )
            ).save()
            backorder_wiz.process()
        else:
            picking.button_validate()

    def _wizard(self, order, handling="proportional", fixed_amount=None):
        vals = {
            "sale_order_ids": [(6, 0, order.ids)],
            "advance_payment_method": "delivered",
            "downpayment_handling": handling,
        }
        if fixed_amount is not None:
            vals["downpayment_fixed_amount"] = fixed_amount
        return self.env["sale.advance.payment.inv"].create(vals)

    def _draft_invoice(self, order):
        return order.invoice_ids.filtered(lambda inv: inv.state == "draft")

    def _dp_line(self, inv):
        return inv.line_ids.filtered(lambda line: line.is_downpayment)

    def test_trigger_detection(self):
        order = self._make_order()
        self._post_dp(order, pct=100.0)
        self._deliver(order, qty=10)

        wiz = self._wizard(order)
        self.assertTrue(wiz.downpayment_exceeds_delivery)
        self.assertEqual(wiz.delivered_ratio, 0.10)
        self.assertEqual(wiz.proportional_downpayment_amount, 100.0)

    def test_no_trigger_full_delivery(self):
        order = self._make_order(qty=10)
        self._post_dp(order, pct=50.0)
        self._deliver(order, qty=10)
        self.assertFalse(self._wizard(order).downpayment_exceeds_delivery)

    def test_no_trigger_dp_less_than_delivery(self):
        order = self._make_order()
        self._post_dp(order, pct=50.0)
        self._deliver(order, qty=80)
        self.assertFalse(self._wizard(order).downpayment_exceeds_delivery)

    def test_no_trigger_non_delivered_methods(self):
        order = self._make_order()
        self._post_dp(order, pct=100.0)
        self._deliver(order, qty=10)
        for method in ("percentage", "fixed"):
            wiz = self.env["sale.advance.payment.inv"].create(
                {
                    "sale_order_ids": [(6, 0, order.ids)],
                    "advance_payment_method": method,
                    "amount": 10.0,
                    "fixed_amount": 100.0,
                }
            )
            self.assertFalse(wiz.downpayment_exceeds_delivery)

    def test_proportional_invoice(self):
        order = self._make_order()
        self._post_dp(order, pct=100.0)
        self._deliver(order, qty=10)
        self._wizard(order).create_invoices()
        inv = self._draft_invoice(order)
        self.assertEqual(inv.move_type, "out_invoice")
        self.assertEqual(sum(self._dp_line(inv).mapped("price_subtotal")), -100.0)
        self.assertEqual(inv.amount_untaxed, 0.0)

    def test_two_partial_deliveries(self):
        order = self._make_order()
        self._post_dp(order, pct=100.0)
        self._deliver(order, qty=25)
        self._wizard(order).create_invoices()
        inv1 = self._draft_invoice(order)
        self.assertEqual(sum(self._dp_line(inv1).mapped("price_subtotal")), -250.0)
        inv1.action_post()
        self._deliver(order, qty=50)
        self._wizard(order).create_invoices()
        inv2 = self._draft_invoice(order)
        self.assertEqual(sum(self._dp_line(inv2).mapped("price_subtotal")), -500.0)

    def test_credit_note_native_behaviour(self):
        order = self._make_order()
        self._post_dp(order, pct=100.0)
        self._deliver(order, qty=10)
        self._wizard(order, handling="credit_note").create_invoices()
        refund = order.invoice_ids.filtered(
            lambda inv: inv.state == "draft" and inv.move_type == "out_refund"
        )
        self.assertTrue(refund)

    def test_fixed_amount_deduction(self):
        order = self._make_order()
        self._post_dp(order, pct=100.0)
        self._deliver(order, qty=10)

        self._wizard(order, handling="fixed", fixed_amount=80.0).create_invoices()
        inv = self._draft_invoice(order)
        self.assertEqual(inv.move_type, "out_invoice")
        self.assertEqual(sum(self._dp_line(inv).mapped("price_subtotal")), -80.0)

    def test_fixed_amount_rejected(self):
        order = self._make_order()
        self._post_dp(order, pct=100.0)
        self._deliver(order, qty=10)
        with self.assertRaises(ValidationError) as m:
            self._wizard(order, handling="fixed", fixed_amount=-50.0).create_invoices()
        self.assertIn("cannot be negative", m.exception.args[0])
        with self.assertRaises(ValidationError) as m:
            self._wizard(order, handling="fixed", fixed_amount=1500.0).create_invoices()
        self.assertIn("cannot exceed", m.exception.args[0])

    def test_full_delivery_defaults_to_remaining_dp(self):
        order = self._make_order()
        self._post_dp(order, pct=100.0)
        self._deliver(order, qty=25)
        wiz = self._wizard(order, handling="fixed")
        self.assertEqual(wiz.downpayment_fixed_amount, 250.0)
        wiz.create_invoices()
        self._draft_invoice(order).action_post()
        self._deliver(order, qty=75)
        wiz = self._wizard(order, handling="fixed")
        self.assertEqual(wiz.downpayment_fixed_amount, 750.0)

    def test_draft_dp_not_counted(self):
        order = self._make_order()
        self._deliver(order, qty=10)

        wiz_dp = self.env["sale.advance.payment.inv"].create(
            {
                "sale_order_ids": [(6, 0, order.ids)],
                "advance_payment_method": "percentage",
                "amount": 100.0,
            }
        )
        wiz_dp.create_invoices()
        wiz = self._wizard(order)
        self.assertFalse(wiz.downpayment_exceeds_delivery)
        self.assertEqual(wiz.total_downpayment_invoiced, 0.0)

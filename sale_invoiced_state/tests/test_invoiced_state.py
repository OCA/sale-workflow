# Copyright 2022 PyTech SRL - Alessandro Uffreduzzi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestInvoicedState(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env.ref("sale_invoiced_state.sale_order_1")

    def invoice_downpayment(self):
        self.env["sale.advance.payment.inv"].with_context(
            active_ids=self.order.ids
        ).create(
            {
                "advance_payment_method": "percentage",
                "amount": 20,
            }
        ).create_invoices()

    def invoice_all(self, deduct_downpayment=True):
        self.env["sale.advance.payment.inv"].with_context(
            active_ids=self.order.ids
        ).create(
            {"advance_payment_method": "all" if deduct_downpayment else "delivered"}
        ).create_invoices()

    def test_draft_order(self):
        self.assertEqual(self.order.invoiced_state, "not_invoiced")

    def test_sent_order(self):
        self.order.state = "sent"
        self.assertEqual(self.order.invoiced_state, "not_invoiced")

    def test_confirmed_order(self):
        self.order.action_confirm()
        self.assertEqual(self.order.invoiced_state, "not_invoiced")

    def test_downpayment(self):
        self.order.action_confirm()
        self.invoice_downpayment()
        self.assertEqual(self.order.invoiced_state, "downpayment")

    def test_partially_invoiced(self):
        self.order.action_confirm()
        self.order.order_line[1].qty_delivered = 2
        self.invoice_all()
        self.assertEqual(self.order.invoiced_state, "partially")

    def test_partially_invoiced_with_downpayment(self):
        self.order.action_confirm()
        self.invoice_downpayment()
        self.order.order_line[1].qty_delivered = 2
        self.invoice_all()
        self.assertEqual(self.order.invoiced_state, "partially")

    def test_fully_invoiced(self):
        self.order.action_confirm()
        for line in self.order.order_line:
            line.qty_delivered = line.product_uom_qty
        self.invoice_all()
        self.assertEqual(self.order.invoiced_state, "invoiced")

    def test_fully_invoiced_with_downpayment_deducted(self):
        self.order.action_confirm()
        self.invoice_downpayment()
        for line in self.order.order_line:
            line.qty_delivered = line.product_uom_qty
        self.invoice_all()
        self.assertEqual(self.order.invoiced_state, "invoiced")

    def test_fully_invoiced_with_downpayment_not_deducted(self):
        self.order.action_confirm()
        self.invoice_downpayment()
        for line in self.order.order_line:
            line.qty_delivered = line.product_uom_qty
        self.invoice_all(deduct_downpayment=False)
        self.assertEqual(self.order.invoiced_state, "partially")

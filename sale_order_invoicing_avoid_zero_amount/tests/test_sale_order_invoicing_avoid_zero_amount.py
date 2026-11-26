# Copyright 2026 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon

from ..hooks import post_init_hook


class TestSaleOrderInvoicingAvoidZeroAmount(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The list price is set explicitly on every product: other modules can
        # recompute the unit price of the line from it
        vals = {"type": "service", "invoice_policy": "order", "taxes_id": False}
        cls.product_free = cls.env["product.product"].create(
            {**vals, "name": "Free service", "list_price": 0}
        )
        cls.product_paid = cls.env["product.product"].create(
            {**vals, "name": "Paid service", "list_price": 10}
        )
        cls.product_free_delivery = cls.env["product.product"].create(
            {
                **vals,
                "name": "Free goods",
                "type": "consu",
                "invoice_policy": "delivery",
                "list_price": 0,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})

    def _create_order(self, *products, **line_vals):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create({"product_id": product.id, **line_vals})
                    for product in products
                ],
            }
        )
        order.action_confirm()
        return order

    def test_zero_amount_order(self):
        order = self._create_order(self.product_free)
        self.assertEqual(order.amount_total, 0)
        self.assertEqual(order.invoice_status, "no")

    def test_price_change_recomputes(self):
        order = self._create_order(self.product_paid)
        self.assertEqual(order.invoice_status, "to invoice")
        order.order_line.price_unit = 0
        self.assertEqual(order.invoice_status, "no")

    def test_mixed_order(self):
        order = self._create_order(self.product_free, self.product_paid)
        self.assertEqual(order.invoice_status, "to invoice")
        invoice = order._create_invoices()
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        self.assertEqual(order.invoice_status, "invoiced")

    def test_zero_price_with_fixed_tax(self):
        tax = self.env["account.tax"].create(
            {"name": "Fixed", "amount_type": "fixed", "amount": 1}
        )
        order = self._create_order(self.product_free, tax_id=[Command.set(tax.ids)])
        self.assertEqual(order.amount_total, 1)
        self.assertEqual(order.invoice_status, "to invoice")

    def test_zero_amount_order_delivery_policy(self):
        order = self._create_order(self.product_free_delivery)
        self.assertEqual(order.invoice_status, "no")
        order.order_line.qty_delivered = 1
        self.assertEqual(order.order_line.qty_to_invoice, 1)
        self.assertEqual(order.invoice_status, "no")

    def test_post_init_hook(self):
        order = self._create_order(self.product_free)
        # Simulate an order confirmed before installing the module
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE sale_order SET invoice_status = 'to invoice' WHERE id = %s",
            (order.id,),
        )
        order.invalidate_recordset(["invoice_status"])
        self.assertEqual(order.invoice_status, "to invoice")
        post_init_hook(self.env)
        self.assertEqual(order.invoice_status, "no")

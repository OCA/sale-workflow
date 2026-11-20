# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_model = self.env["res.partner"]
        self.sale_order_model = self.env["sale.order"]

        # Create test customer
        self.customer = self.partner_model.create(
            {
                "name": "Test Customer",
                "customer_rank": 1,
            }
        )

        # Create test product
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "sale_ok": True,
            }
        )

    def _create_order(self, date_order, price_unit):
        return self.sale_order_model.create(
            {
                "partner_id": self.customer.id,
                "date_order": date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": price_unit,
                        },
                    )
                ],
            }
        )

    def test_last_sale_order_tracking(self):
        """The customer shows its most recent confirmed sale order"""
        # Initially, no sale orders
        self.assertFalse(self.customer.last_sale_order_date)
        self.assertFalse(self.customer.last_sale_order_id)

        # A quotation alone does not count as a sale
        quotation = self._create_order("2025-01-01 10:00:00", 100)
        self.assertFalse(self.customer.last_sale_order_id)

        # Confirming the order makes it the last sale
        quotation.action_confirm()
        self.assertEqual(self.customer.last_sale_order_id, quotation)
        self.assertEqual(self.customer.last_sale_order_date, quotation.date_order)

        # A newer confirmed order replaces it
        newer_order = self._create_order("2025-01-15 10:00:00", 200)
        newer_order.action_confirm()
        self.assertEqual(self.customer.last_sale_order_id, newer_order)

        # Cancelling the latest order falls back to the previous one
        newer_order.with_context(disable_cancel_warning=True).action_cancel()
        self.assertEqual(self.customer.last_sale_order_id, quotation)

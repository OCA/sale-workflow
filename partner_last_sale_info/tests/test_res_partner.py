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

    def test_last_sale_order_date_computation(self):
        """Test that last sale order date is computed correctly"""
        # Initially, no sale orders
        self.assertFalse(self.customer.last_sale_order_date)
        self.assertFalse(self.customer.last_sale_order_id)

        # Create a sale order
        sale_order1 = self.sale_order_model.create(
            {
                "partner_id": self.customer.id,
                "date_order": "2025-01-01 10:00:00",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

        # Confirm the order to make it visible to the computation
        sale_order1.action_confirm()

        # Check that last sale order date is updated
        self.customer._compute_last_sale_order_date()
        self.assertTrue(self.customer.last_sale_order_date)
        self.assertEqual(self.customer.last_sale_order_id, sale_order1.id)

        # Create another sale order with later date
        sale_order2 = self.sale_order_model.create(
            {
                "partner_id": self.customer.id,
                "date_order": "2025-01-15 10:00:00",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 200,
                        },
                    )
                ],
            }
        )

        # Confirm the second order
        sale_order2.action_confirm()

        # Check that last sale order date is updated to the newer one
        self.customer._compute_last_sale_order_date()
        self.assertEqual(self.customer.last_sale_order_id, sale_order2.id)

        # Cancel the latest order and check it's not counted
        sale_order2.action_cancel()
        self.customer._compute_last_sale_order_date()
        self.assertEqual(self.customer.last_sale_order_id, sale_order1.id)

        # Confirm the first order and verify it's tracked
        sale_order1.action_confirm()
        self.customer._compute_last_sale_order_date()
        self.assertEqual(self.customer.last_sale_order_id, sale_order1.id)

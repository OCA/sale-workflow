# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleOrer(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
                "list_price": 100,
            }
        )

        self.payment_term_id = self.env["account.payment.term"].create(
            {
                "name": "Test Payment Term",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "value_amount": 100,
                            "value": "percent",
                        },
                    )
                ],
            }
        )

        self.payment_term_id2 = self.env["account.payment.term"].create(
            {
                "name": "Test Payment Term 2",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "value_amount": 100,
                            "value": "percent",
                        },
                    )
                ],
            }
        )

    def test_sale_order(self):
        sale_order1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    ),
                ],
                "payment_term_id": self.payment_term_id.id,
            }
        )

        sale_order2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    ),
                ],
                "payment_term_id": self.payment_term_id2.id,
            }
        )

        sale_order1.action_confirm()
        sale_order2.action_confirm()

        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=[sale_order1.id, sale_order2.id])
            .create({})
        )

        wizard.create_invoices()

        invoices = self.env["account.move"].search(
            [
                ("partner_id", "=", self.partner.id),
            ]
        )

        self.assertEqual(len(invoices), 2)

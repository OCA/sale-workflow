# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.exceptions import ValidationError

from .common import SaleOrderBlanketOrderCase


class TestSaleBlanketOrder(SaleOrderBlanketOrderCase):
    def test_constrains(self):
        # Create a call-off order
        with self.assertRaisesRegex(
            ValidationError, "The validity start date is required"
        ):
            self.env["sale.order"].create(
                {
                    "order_type": "blanket",
                    "partner_id": self.partner.id,
                }
            )
        with self.assertRaisesRegex(
            ValidationError, "The validity end date is required"
        ):
            self.env["sale.order"].create(
                {
                    "order_type": "blanket",
                    "partner_id": self.partner.id,
                    "blanket_validity_start_date": "2024-01-01",
                }
            )
        with self.assertRaisesRegex(
            ValidationError, "The validity end date must be greater than"
        ):
            self.env["sale.order"].create(
                {
                    "order_type": "blanket",
                    "partner_id": self.partner.id,
                    "blanket_validity_start_date": "2024-01-02",
                    "blanket_validity_end_date": "2024-01-01",
                }
            )
        with self.assertRaisesRegex(
            ValidationError, "A blanket order cannot have a blanket order."
        ):
            self.env["sale.order"].create(
                {
                    "order_type": "blanket",
                    "partner_id": self.partner.id,
                    "blanket_validity_start_date": "2024-01-01",
                    "blanket_validity_end_date": "2024-12-31",
                    "blanket_order_id": self.so.id,
                }
            )

    def test_no_product_overlap(self):
        # Create a blanket order with a product that is already in the blanket order
        with self.assertRaisesRegex(
            ValidationError,
            (
                "The product 'Product 1' is already part of another blanket order "
                f"{self.blanket_so.name}."
            ),
        ):
            self.env["sale.order"].create(
                {
                    "order_type": "blanket",
                    "partner_id": self.partner.id,
                    "blanket_validity_start_date": "2024-02-01",
                    "blanket_validity_end_date": "2025-01-31",
                    "order_line": [
                        Command.create(
                            {"product_id": self.product_1.id, "product_uom_qty": 10.0}
                        ),
                    ],
                }
            )

    def test_reservation(self):
        # Confirm the blanket order with reservation at call off
        self.blanket_so.action_confirm()
        self.assertEqual(self.blanket_so.state, "sale")
        self.assertEqual(
            self.blanket_so.commitment_date.date(),
            self.blanket_so.blanket_validity_start_date,
        )
        self.assertFalse(self.blanket_so.order_line.move_ids)

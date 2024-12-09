# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import freezegun

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import RecordCapturer

from .common import SaleOrderBlanketOrderCase


class TestSaleBlanketOrder(SaleOrderBlanketOrderCase):
    def test_confirm_start_date_required(self):
        order = self.env["sale.order"].create(
            {
                "order_type": "blanket",
                "partner_id": self.partner.id,
            }
        )
        # Create a call-off order
        with self.assertRaisesRegex(
            ValidationError, "The validity start date is required"
        ):
            order.action_confirm()

    def test_confirm_end_date_required(self):
        order = self.env["sale.order"].create(
            {
                "order_type": "blanket",
                "partner_id": self.partner.id,
                "blanket_validity_start_date": "2024-01-01",
            }
        )
        with self.assertRaisesRegex(
            ValidationError, "The validity end date is required"
        ):
            order.action_confirm()

    def test_confrim_end_date_greater_than_start_date(self):
        order = self.env["sale.order"].create(
            {
                "order_type": "blanket",
                "partner_id": self.partner.id,
                "blanket_validity_start_date": "2024-01-02",
                "blanket_validity_end_date": "2024-01-01",
            }
        )
        with self.assertRaisesRegex(
            ValidationError, "The validity end date must be greater than"
        ):
            order.action_confirm()

    def test_confirm_no_blanket_order(self):
        order = self.env["sale.order"].create(
            {
                "order_type": "blanket",
                "partner_id": self.partner.id,
                "blanket_validity_start_date": "2024-01-01",
                "blanket_validity_end_date": "2024-12-31",
                "blanket_order_id": self.so.id,
            }
        )
        with self.assertRaisesRegex(
            ValidationError, "A blanket order cannot have a blanket order."
        ):
            order.action_confirm()

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

    def test_eol(self):
        # Confirm the blanket order with reservation at call off
        self.assertFalse(self.blanket_so.blanket_need_to_be_finalized)
        self.blanket_so.blanket_eol_strategy = "deliver"
        self.blanket_so.action_confirm()
        self.assertTrue(self.blanket_so.blanket_need_to_be_finalized)
        self.blanket_so.flush_recordset()
        with RecordCapturer(
            self.so_model, self.call_off_domain
        ) as captured, freezegun.freeze_time("2026-12-31"):
            self.so_model._cron_manage_blanket_order_eol()
        self.assertFalse(self.blanket_so.blanket_need_to_be_finalized)
        self.assertEqual(len(captured.records), 1)
        for line in self.blanket_so.order_line:
            self.assertEqual(line.call_off_remaining_qty, 0.0)
            call_off = line.call_off_line_ids
            self.assertEqual(len(call_off), 1)
            self.assertEqual(call_off.product_uom_qty, line.product_uom_qty)
            self.assertTrue(line.move_ids)

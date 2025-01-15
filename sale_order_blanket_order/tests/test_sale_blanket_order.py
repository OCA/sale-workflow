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
        self.blanket_so.action_confirm()
        order = self.env["sale.order"].create(
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
        # Validate a blanket order with a product that is already in the blanket order
        with self.assertRaisesRegex(
            ValidationError,
            (
                "The product 'Product 1' is already part of another blanket order "
                f"{self.blanket_so.name}."
            ),
        ):
            order.action_confirm()

    def test_reservation(self):
        # Confirm the blanket order with reservation at call off
        self.blanket_so.action_confirm()
        self.assertTrue(self.blanket_so.manual_delivery)
        self.assertEqual(self.blanket_so.state, "sale")
        self.assertEqual(
            self.blanket_so.commitment_date.date(),
            self.blanket_so.blanket_validity_start_date,
        )
        self.assertFalse(self.blanket_so.order_line.move_ids)

    def test_reset_reservation_at_cancel(self):
        self.blanket_so.action_confirm()
        self.assertTrue(self.blanket_so.manual_delivery)
        self.blanket_so._action_cancel()
        self.assertFalse(self.blanket_so.manual_delivery)

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

    def test_eol_with_call_off_in_progress(self):
        self.assertFalse(self.blanket_so.blanket_need_to_be_finalized)
        self.blanket_so.blanket_eol_strategy = "deliver"
        self.blanket_so.action_confirm()
        self.assertTrue(self.blanket_so.blanket_need_to_be_finalized)
        self.blanket_so.flush_recordset()
        # we create a call-of order for part of the quantity of
        # the product 1
        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "date_order": "2025-02-01",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 5.0,
                        }
                    ),
                ],
            }
        )
        with freezegun.freeze_time("2025-11-12"):
            order.action_confirm()

        self.assertEqual(self.blanket_so.blanket_need_to_be_finalized, True)
        with RecordCapturer(
            self.so_model, self.call_off_domain
        ) as captured, freezegun.freeze_time("2026-12-31"):
            self.so_model._cron_manage_blanket_order_eol()
        self.assertFalse(self.blanket_so.blanket_need_to_be_finalized)
        self.assertEqual(len(captured.records), 1)
        new_call_off = captured.records[0]
        for line in self.blanket_so.order_line:
            self.assertEqual(line.call_off_remaining_qty, 0.0)
            call_off = line.call_off_line_ids
            if line.product_id == self.product_2:
                # 2 call-off lines should exist
                # one for the call-off order created in the past
                # and one for the new call-off order created by the cron
                self.assertEqual(len(call_off), 2)
                self.assertEqual(call_off.order_id, order | new_call_off)
                self.assertEqual(
                    set(call_off.mapped("product_uom_qty")),
                    {5, line.product_uom_qty - 5},
                )
            else:
                self.assertEqual(len(call_off), 1)
                self.assertEqual(call_off.product_uom_qty, line.product_uom_qty)
            self.assertTrue(line.move_ids)

    def test_reservation_strategy_editable(self):
        # change is allowed in draft state
        self.blanket_so.blanket_reservation_strategy = "fake"
        self.blanket_so.blanket_reservation_strategy = "at_call_off"
        self.blanket_so.action_confirm()
        # change is allowed after confirmation while the blanket order
        # is not finalized
        self.blanket_so.blanket_reservation_strategy = "fake"
        self.blanket_so._action_cancel()
        with self.assertRaisesRegex(
            ValidationError, "The reservation strategy cannot be modified"
        ), self.env.cr.savepoint():
            # change is not allowed on canceled order
            self.blanket_so.blanket_reservation_strategy = "at_call_off"
        self.blanket_so.action_draft()
        # change is allowed in draft state
        self.blanket_so.blanket_reservation_strategy = "at_call_off"
        self.blanket_so.action_confirm()
        with freezegun.freeze_time("2026-12-31"):
            self.so_model._cron_manage_blanket_order_eol()

        self.assertFalse(self.blanket_so.blanket_need_to_be_finalized)
        with self.assertRaisesRegex(
            ValidationError, "The reservation strategy cannot be modified"
        ), self.env.cr.savepoint():
            # change is not allowed on finalized order
            self.blanket_so.blanket_reservation_strategy = "fake"

    def test_eol_strategy_editable(self):
        # change is allowed in draft state
        self.blanket_so.blanket_eol_strategy = "deliver"
        self.blanket_so.blanket_eol_strategy = False
        self.blanket_so.action_confirm()
        # change is allowed after confirmation while the blanket order
        # is not finalized
        self.blanket_so.blanket_eol_strategy = "deliver"
        self.blanket_so._action_cancel()
        with self.assertRaisesRegex(
            ValidationError, "The end-of-life strategy cannot be modified"
        ), self.env.cr.savepoint():
            # change is not allowed on canceled order
            self.blanket_so.blanket_eol_strategy = False
        self.blanket_so.action_draft()
        # change is allowed in draft state
        self.blanket_so.blanket_eol_strategy = False
        self.blanket_so.action_confirm()
        with freezegun.freeze_time("2026-12-31"):
            self.so_model._cron_manage_blanket_order_eol()

        self.assertFalse(self.blanket_so.blanket_need_to_be_finalized)
        with self.assertRaisesRegex(
            ValidationError, "The end-of-life strategy cannot be modified"
        ), self.env.cr.savepoint():
            # change is not allowed on finalized order
            self.blanket_so.blanket_eol_strategy = "deliver"

    def test_update_qty(self):
        self.blanket_so.action_confirm()
        so_line_product_2 = self.blanket_so.order_line.filtered(
            lambda l: l.product_id == self.product_2
        )
        self.assertEqual(so_line_product_2.product_uom_qty, 10)
        so_line_product_2.product_uom_qty = 5
        self.assertEqual(so_line_product_2.product_uom_qty, 5)
        self.assertEqual(so_line_product_2.call_off_remaining_qty, 5)
        # if we deliver 3, we should not update the qty under the remaining qty
        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "date_order": "2025-02-01",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 3.0,
                        }
                    ),
                ],
            }
        )
        with freezegun.freeze_time("2025-02-01"):
            order.action_confirm()
        self.assertEqual(so_line_product_2.call_off_remaining_qty, 2)
        with self.assertRaisesRegex(
            ValidationError, "The forecasted quantity cannot be less than the quantity"
        ):
            so_line_product_2.product_uom_qty = 1

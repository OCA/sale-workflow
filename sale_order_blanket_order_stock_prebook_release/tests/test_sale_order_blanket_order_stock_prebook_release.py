# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

import freezegun

from odoo import Command

from .common import SaleOrderBlanketOrderStockPrebookReleaseCase


class TestSaleOrderBlanketOrderStockPrebookRelease(
    SaleOrderBlanketOrderStockPrebookReleaseCase
):
    def test_blanket_move_date_priority(self):
        self.assertFalse(self.blanket_so.blanket_move_date_priority)

        # the move date priority is computed when the blanket order is confirmed
        self.blanket_so.action_confirm()
        self.assertTrue(self.blanket_so.blanket_move_date_priority)
        # the move date priority must be the validity start date of the blanket order
        # incremented by the x seconds where x is the number of confirmed blanket orders
        # with the same validity start date
        # At this point we have only one confirmed blanket order with the same validity
        # start date
        move_date_priority = self.blanket_so.blanket_move_date_priority
        self.assertEqual(
            move_date_priority,
            self._date_to_datetime(
                self.blanket_so.blanket_validity_start_date, nb_seconds=0
            ),
        )
        # if we create a new blanket order with the same validity start date and confirm it
        # the move date priority of the first blanket order must be incremented by 1 second
        new_blanket_so = self.env["sale.order"].create(
            {
                "order_type": "blanket",
                "partner_id": self.partner_delta.id,
                "blanket_validity_start_date": "2025-01-01",
                "blanket_validity_end_date": "2025-12-31",
                "blanket_reservation_strategy": "at_confirm",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )
        new_blanket_so.action_confirm()
        self.assertEqual(
            new_blanket_so.blanket_move_date_priority,
            self._date_to_datetime(
                new_blanket_so.blanket_validity_start_date, nb_seconds=1
            ),
        )

        # if we create a new blanket order with a different validity start date
        # the move date priority of the first blanket order must be the validity start date
        # incremented by 0 seconds
        new_blanket_so = self.env["sale.order"].create(
            {
                "order_type": "blanket",
                "partner_id": self.partner_delta.id,
                "blanket_validity_start_date": "2026-01-01",
                "blanket_validity_end_date": "2026-12-31",
                "blanket_reservation_strategy": "at_confirm",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )
        new_blanket_so.action_confirm()
        self.assertEqual(
            new_blanket_so.blanket_move_date_priority,
            self._date_to_datetime(
                new_blanket_so.blanket_validity_start_date, nb_seconds=0
            ),
        )

    def test_date_priority_on_prebook_moves(self):
        """For blanket oders, the prebook moves must have the date priority set to the blanket
        move date priority"""
        self.blanket_so.action_confirm()
        prebook_moves = self.blanket_so.order_line.move_ids.filtered(
            "used_for_sale_reservation"
        )
        self.assertTrue(prebook_moves)
        for move in prebook_moves:
            self.assertEqual(
                move.date_priority, self.blanket_so.blanket_move_date_priority
            )

    def test_date_priority_on_prebook_moves_2(self):
        """For normal order, in case of prebooking, the date priority must be the datetime at
        confirmation"""
        new_so = self.env["sale.order"].create(
            {
                "partner_id": self.partner_delta.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom_qty": 10.0,
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )
        with freezegun.freeze_time("2020-01-01 00:00:00"):
            new_so.reserve_stock()
            now = datetime(2020, 1, 1, 0, 0, 0)
            prebook_moves = new_so.order_line.move_ids.filtered(
                "used_for_sale_reservation"
            )
            self.assertTrue(prebook_moves)
            for move in prebook_moves:
                self.assertEqual(move.date_priority, now)

    def test_date_priority_on_preparation_moves(self):
        """For blanket oders, the preparation moves must have the date priority set to the
        blanket move date priority"""
        self.blanket_so.action_confirm()

        with freezegun.freeze_time("2025-02-01"):
            order = self.env["sale.order"].create(
                {
                    "order_type": "call_off",
                    "partner_id": self.partner_delta.id,
                    "blanket_order_id": self.blanket_so.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.product1.id,
                                "product_uom_qty": 10.0,
                            }
                        ),
                    ],
                }
            )
            order.action_confirm()

        # the date_priority on the moves linked to the blanket order
        # for the preparation must be blanket_move_date_priority
        self.assertTrue(
            order.order_line.blanket_move_ids.filtered(
                lambda m: not m.used_for_sale_reservation
            )
        )
        for move in order.order_line.blanket_move_ids:
            self.assertEqual(
                move.date_priority, self.blanket_so.blanket_move_date_priority
            )

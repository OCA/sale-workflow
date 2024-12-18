# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import freezegun

from odoo import Command

from .common import SaleOrderBlanketOrderCase


class TestSaleBlanketOrder(SaleOrderBlanketOrderCase):
    def _get_current_moves(self, so, product=False, only_reservation=False):
        moves = so.order_line.move_ids.filtered(lambda m: m.state == "confirmed")
        if product:
            moves = moves.filtered(lambda m: m.product_id == product)
        if only_reservation:
            moves = moves.filtered("used_for_sale_reservation")
        return moves

    def test_reservation_at_confirm(self):
        # Confirm the blanket order with reservation at confirm
        self.assertFalse(self.blanket_so.order_line.move_ids)
        self.blanket_so.action_confirm()
        self.assertEqual(self.blanket_so.state, "sale")
        self.assertEqual(
            self.blanket_so.commitment_date.date(),
            self.blanket_so.blanket_validity_start_date,
        )
        self.assertTrue(
            all(self.blanket_so.order_line.move_ids.mapped("used_for_sale_reservation"))
        )

    def test_change_reservation_mode(self):
        self.blanket_so.action_confirm()
        self.assertTrue(
            all(self.blanket_so.order_line.move_ids.mapped("used_for_sale_reservation"))
        )
        self.blanket_so.blanket_reservation_strategy = "at_call_off"
        moves = self._get_current_moves(self.blanket_so, only_reservation=True)
        self.assertFalse(moves)
        self.blanket_so.blanket_reservation_strategy = "at_confirm"
        moves = self._get_current_moves(self.blanket_so, only_reservation=True)
        self.assertTrue(moves)

    def test_update_reservation(self):
        self.blanket_so.action_confirm()
        so_line_product_2 = self.blanket_so.order_line.filtered(
            lambda l: l.product_id == self.product_2
        )
        moves = self._get_current_moves(
            self.blanket_so, self.product_2, only_reservation=True
        )
        reserved_qty = sum(moves.mapped("product_uom_qty"))
        self.assertEqual(reserved_qty, 10)
        so_line_product_2.product_uom_qty = 5.0
        moves = self._get_current_moves(
            self.blanket_so, self.product_2, only_reservation=True
        )
        reserved_qty = sum(moves.mapped("product_uom_qty"))
        self.assertEqual(reserved_qty, 5)

        so_line_product_2.product_uom_qty = 15.0
        moves = self._get_current_moves(
            self.blanket_so, self.product_2, only_reservation=True
        )
        reserved_qty = sum(moves.mapped("product_uom_qty"))
        self.assertEqual(reserved_qty, 15)

    def test_update_current_reservation_with_delivered_qty(self):
        self.blanket_so.action_confirm()
        so_line_product_2 = self.blanket_so.order_line.filtered(
            lambda l: l.product_id == self.product_2
        )
        moves = self._get_current_moves(
            self.blanket_so, self.product_2, only_reservation=True
        )
        reserved_qty = sum(moves.mapped("product_uom_qty"))
        self.assertEqual(reserved_qty, 10)
        so_line_product_2.product_uom_qty = 5.0
        moves = self._get_current_moves(
            self.blanket_so, self.product_2, only_reservation=True
        )
        reserved_qty = sum(moves.mapped("product_uom_qty"))
        self.assertEqual(reserved_qty, 5)

        # create and process a call-off
        with freezegun.freeze_time("2025-02-01"):
            order = self.env["sale.order"].create(
                {
                    "order_type": "call_off",
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
            order.action_confirm()
        self.assertIn(order.state, ["sale", "done"])

        # update the quantity of the blanket order
        so_line_product_2.product_uom_qty = 15.0
        moves = self._get_current_moves(
            self.blanket_so, self.product_2, only_reservation=True
        )
        reserved_qty = sum(moves.mapped("product_uom_qty"))
        self.assertEqual(reserved_qty, 10)

    @freezegun.freeze_time("2025-02-01")
    def test_change_reservation_mode_partially_processed(self):
        # in this test we create a call-off to partially deliver
        # the product.
        # We change the reservaltion mode from at_conffirm to
        # at_call_off and back.
        # At the end the reserved qty should be the remaining for
        # call off order
        self.blanket_so.action_confirm()
        moves = self._get_current_moves(
            self.blanket_so, self.product_1, only_reservation=True
        )
        reserved_qty = sum(moves.mapped("product_uom_qty"))
        self.assertEqual(reserved_qty, 20)

        # create and process to the delivery of a call off
        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 5.0,
                        }
                    ),
                ],
            }
        )
        order.action_confirm()
        self.assertIn(order.state, ["sale", "done"])

        # at this stage we must still have a reservation for 15
        moves = self._get_current_moves(
            self.blanket_so, self.product_1, only_reservation=True
        )
        reserved_qty = sum(moves.mapped("product_uom_qty"))
        self.assertEqual(reserved_qty, 15)

        # process the picking
        picking = order.order_line.blanket_move_ids.picking_id
        picking.action_assign()
        for move_line in picking.move_line_ids:
            move_line.qty_done = move_line.reserved_uom_qty
        picking._action_done()

        # change reservation mode
        self.blanket_so.blanket_reservation_strategy = "at_call_off"
        moves = self._get_current_moves(
            self.blanket_so, self.product_1, only_reservation=True
        )
        self.assertFalse(moves)

        # back to at_confirm
        self.blanket_so.blanket_reservation_strategy = "at_confirm"
        moves = self._get_current_moves(
            self.blanket_so, self.product_1, only_reservation=True
        )
        reserved_qty = sum(moves.mapped("product_uom_qty"))
        self.assertEqual(reserved_qty, 15)

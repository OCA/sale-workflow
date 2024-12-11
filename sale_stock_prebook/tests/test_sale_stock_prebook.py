# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import UserError, ValidationError

from .common import TestSaleStockPrebookCase


class TestStockReserveSale(TestSaleStockPrebookCase):
    def test_10_reserve_and_release(self):
        self.sale.reserve_stock()
        self.sale2.reserve_stock()
        self.assertTrue(self.sale.stock_is_reserved)
        self.assertFalse(self.sale2.stock_is_reserved)
        reservation_pickings = self.sale._get_reservation_pickings()
        self.assertEqual(
            len(reservation_pickings),
            1,
            "There should be one reservation picking created",
        )
        self.assertEqual(
            len(self.sale.picking_ids), 1, "There should be only one picking created"
        )
        self.assertEqual(self.sale.picking_ids.move_ids.product_id, self.product_1)
        self.assertFalse(self.sale2.picking_ids)
        self.sale.release_reservation()
        reservation_pickings = self.sale._get_reservation_pickings()
        self.assertFalse(self.sale.stock_is_reserved)
        self.assertEqual(
            len(reservation_pickings), 0, "There should be no reservation picking"
        )
        self.assertEqual(len(self.sale.picking_ids), 0, "There should be no picking")

    def test_20_confirmation_release(self):
        self.sale.reserve_stock()
        self.sale.action_confirm()
        self.assertFalse(self.sale.stock_is_reserved)

    def test_30_cancelation_release(self):
        self.sale.reserve_stock()
        self.sale.action_cancel()
        self.assertFalse(self.sale.stock_is_reserved)

    def test_40_action_assign(self):
        self.sale.reserve_stock()
        self.sale.picking_ids.move_ids._action_assign()
        self.assertEqual(self.sale.picking_ids.move_ids.state, "confirmed")
        self.assertFalse(self.sale.picking_ids.move_ids.move_line_ids)
        with self.assertRaises(UserError):
            self.sale.picking_ids.button_validate()

    def test_50_process_move(self):
        self.sale.reserve_stock()
        with self.assertRaisesRegex(ValidationError, "You cannot set a quantity done"):
            self.sale.picking_ids.move_ids.quantity_done = 3

    def test_60_prebook_dedicatd_picking_type(self):
        self.deliver_route.rule_ids.write(
            {"prebook_picking_type_id": self.prebook_picking_type.id}
        )
        self.sale.reserve_stock()
        self.assertEqual(
            self.sale.picking_ids.picking_type_id, self.prebook_picking_type
        )

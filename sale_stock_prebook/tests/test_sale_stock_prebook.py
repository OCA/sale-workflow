# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import TestSaleStockPrebookCase


@tagged("post_install", "-at_install")
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
        self.assertEqual(self.sale.picking_ids.move_lines.product_id, self.product_1)
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
        self.sale.picking_ids.move_lines._action_assign()
        self.assertEqual(self.sale.picking_ids.move_lines.state, "confirmed")
        self.assertFalse(self.sale.picking_ids.move_lines.move_line_ids)
        with self.assertRaises(UserError):
            self.sale.picking_ids.button_validate()

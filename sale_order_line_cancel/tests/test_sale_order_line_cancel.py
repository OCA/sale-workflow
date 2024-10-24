# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestSaleOrderLineCancelBase


class TestSaleOrderLineCancel(TestSaleOrderLineCancelBase):
    def test_cancel_remaining_qty_not_started_picking(self):
        line = self.sale.order_line
        self.assertEqual(line.product_qty_remains_to_deliver, 10)
        self.assertEqual(line.product_qty_canceled, 0)
        self.wiz.with_context(
            active_id=line.id, active_model="sale.order.line"
        ).cancel_remaining_qty()
        self.assertEqual(line.product_qty_remains_to_deliver, 0)
        self.assertEqual(line.product_qty_canceled, 10)

    def test_cancel_backorder(self):
        """check canceled qty set when backorder canceled"""
        sale2 = self._add_done_sale_order(picking_policy="one")
        line = sale2.order_line
        ship = sale2.picking_ids
        ship.move_ids.move_line_ids.qty_done = 5
        ship.with_context(cancel_backorder=True)._action_done()
        self.assertEqual(ship.state, "done")
        self.assertEqual(line.product_qty_canceled, 5)
        self.assertEqual(line.product_qty_remains_to_deliver, 0)

    def test_keep_backorder(self):
        """check canceled qty set when backorder canceled"""
        sale2 = self._add_done_sale_order(picking_policy="one")
        line = sale2.order_line
        ship = sale2.picking_ids
        ship.move_ids.move_line_ids.qty_done = 5
        ship.with_context(cancel_backorder=False)._action_done()
        self.assertEqual(ship.state, "done")
        self.assertEqual(line.product_qty_canceled, 0)
        self.assertEqual(line.product_qty_remains_to_deliver, 5)

    def test_cancel_remaining_qty(self):
        """check the outgoing pick is canceled"""
        ship = self.sale.picking_ids
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 10)
        self.wiz.with_context(
            active_id=self.sale.order_line.id, active_model="sale.order.line"
        ).cancel_remaining_qty()
        self.assertEqual(ship.state, "cancel")
        self.assertEqual(self.sale.order_line.product_qty_canceled, 10)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)

    def test_cancel_pickings(self):
        """if picking is canceled product_qty_canceled increased"""
        self.assertTrue(self.sale.order_line.can_cancel_remaining_qty)
        self.sale.picking_ids.action_cancel()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 10)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)
        self.assertFalse(self.sale.order_line.can_cancel_remaining_qty)
        self.wiz.with_context(
            active_id=self.sale.order_line.id, active_model="sale.order.line"
        ).cancel_remaining_qty()

    def test_cancel_move_kit(self):
        """when all remaining moves are canceled product_qty_canceled increased"""
        self.assertTrue(self.sale.order_line.can_cancel_remaining_qty)
        move = self.sale.picking_ids.move_ids
        self.assertEqual(move.sale_line_id, self.sale.order_line)
        # simulate a kit with a second move linked to the sale SO line
        move2 = move.copy()
        move2._action_confirm()
        self.assertEqual(move2.sale_line_id, self.sale.order_line)
        move._action_cancel()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 0)
        move2._action_cancel()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 10)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)
        self.assertFalse(self.sale.order_line.can_cancel_remaining_qty)
        self.wiz.with_context(
            active_id=self.sale.order_line.id, active_model="sale.order.line"
        ).cancel_remaining_qty()

    def test_reset_to_draft(self):
        ship = self.sale.picking_ids
        ship.action_assign()
        ship.move_ids.move_line_ids.qty_done = 5
        ship.with_context(cancel_backorder=True)._action_done()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 5)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)
        self.sale.with_context(disable_cancel_warning=True).action_cancel()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 5)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)
        self.sale.action_draft()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 0)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 5)

    def test_reset_to_draft_after_cancel(self):
        ship = self.sale.picking_ids
        ship.action_assign()
        ship.move_ids.move_line_ids.qty_done = 5
        ship.with_context(cancel_backorder=False)._action_done()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 0)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 5)
        self.wiz.with_context(
            active_id=self.sale.order_line.id, active_model="sale.order.line"
        ).cancel_remaining_qty()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 5)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)
        self.sale.with_context(disable_cancel_warning=True).action_cancel()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 5)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)
        self.sale.action_draft()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 0)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 5)

# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import freezegun

from odoo import Command

from .common import SaleOrderBlanketOrderCase


@freezegun.freeze_time("2025-02-01")
class TestSaleCallOffOrderProcessing(SaleOrderBlanketOrderCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blanket_so.action_confirm()

    def test_no_reservation_processing(self):
        # Create a call-off order without reservation
        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                ],
            }
        )
        order.action_confirm()
        self.assertIn(order.state, ["sale", "done"])
        self.assertRecordValues(
            order.order_line,
            [
                {
                    "product_uom_qty": 10.0,
                    "price_unit": 0.0,
                    "qty_to_deliver": 0.0,
                    "qty_to_invoice": 0.0,
                    "qty_delivered": 0.0,
                    "display_qty_widget": False,
                },
                {
                    "product_uom_qty": 10.0,
                    "price_unit": 0.0,
                    "qty_to_deliver": 0.0,
                    "qty_to_invoice": 0.0,
                    "qty_delivered": 0.0,
                    "display_qty_widget": False,
                },
            ],
        )

        # The lines should be linked to moves linked to a blanked order line
        for line in order.order_line:
            self.assertTrue(line.blanket_move_ids)
            sale_line = line.blanket_move_ids.sale_line_id
            self.assertEqual(sale_line.product_id, line.product_id)
            self.assertEqual(sale_line.order_id, self.blanket_so)

        # process the picking
        picking = line.blanket_move_ids.picking_id
        picking.action_assign()
        for move_line in picking.move_line_ids:
            move_line.qty_done = move_line.reserved_uom_qty
        picking._action_done()

        blanket_lines = self.blanket_so.order_line

        # part of the quantity into the blanket order are now delivered
        for product in [self.product_1, self.product_2]:
            self.assertEqual(
                sum(
                    blanket_lines.filtered(lambda l: l.product_id == product).mapped(
                        "qty_delivered"
                    )
                ),
                10.0,
            )

    def test_no_reservation_processing_2(self):
        # In this test we create a call-off order with 1 lines
        # for product 1 where the quantity to deliver is greater
        # than the quantity defined per line in the blanket order.
        # On the blanket order we have 2 lines for product 1 with
        # 10.0 quantity each.
        # The call-off order will have 1 line for product 1 with
        # 15.0 quantity.

        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 15.0,
                        }
                    ),
                ],
            }
        )
        order.action_confirm()
        self.assertIn(order.state, ["sale", "done"])

        # process the picking
        picking = order.order_line.blanket_move_ids.picking_id
        picking.action_assign()
        for move_line in picking.move_line_ids:
            move_line.qty_done = move_line.reserved_uom_qty
        picking._action_done()

        blanket_lines = self.blanket_so.order_line
        self.assertEqual(
            sum(
                blanket_lines.filtered(lambda l: l.product_id == self.product_1).mapped(
                    "qty_delivered"
                )
            ),
            15.0,
        )


@freezegun.freeze_time("2025-02-01")
class TestSaleAutoDoneCallOffOrderProcessing(TestSaleCallOffOrderProcessing):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("sale.group_auto_done_setting")

# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import freezegun

from odoo import Command
from odoo.exceptions import ValidationError

from .common import SaleOrderBlanketOrderCase


class TestSaleCallOffOrder(SaleOrderBlanketOrderCase):
    def test_order_constrains(self):
        # Create a call-off order
        with self.assertRaisesRegex(
            ValidationError, "A call-off order must have a blanket order."
        ):
            self.env["sale.order"].create(
                {
                    "order_type": "call_off",
                    "partner_id": self.partner.id,
                }
            )
        with self.assertRaisesRegex(
            ValidationError, "A call-off order must have a blanket order."
        ):
            self.env["sale.order"].create(
                {
                    "order_type": "call_off",
                    "partner_id": self.partner.id,
                    "blanket_order_id": self.so.id,
                }
            )
        with self.assertRaisesRegex(
            ValidationError, "The blanket order must be confirmed"
        ):
            self.env["sale.order"].create(
                {
                    "order_type": "call_off",
                    "partner_id": self.partner.id,
                    "blanket_order_id": self.blanket_so.id,
                }
            )

        self.blanket_so.action_confirm()
        with self.assertRaisesRegex(
            ValidationError,
            (
                "The call-off order must be within the "
                "validity period of the blanket order."
            ),
        ):
            self.env["sale.order"].create(
                {
                    "order_type": "call_off",
                    "date_order": "2024-01-01",
                    "partner_id": self.partner.id,
                    "blanket_order_id": self.blanket_so.id,
                }
            )

        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "date_order": "2025-02-01",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
            }
        )
        self.assertTrue(order)

    @freezegun.freeze_time("2025-02-01")
    def test_order_line_constrains(self):
        self.blanket_so.action_confirm()

        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_3.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                ],
            }
        )
        with self.assertRaisesRegex(
            ValidationError,
            ("The product is not part of linked blanket order"),
        ), self.env.cr.savepoint():
            order.action_confirm()

        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 100.0,
                        }
                    ),
                ],
            }
        )
        with self.assertRaisesRegex(
            ValidationError,
            (
                "The quantity to procure is greater than the quantity remaining "
                "to deliver"
            ),
        ), self.env.cr.savepoint():
            order.action_confirm()

    def test_order_line_attributes(self):
        self.blanket_so.action_confirm()
        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "date_order": "2025-02-01",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                ],
            }
        )
        blanket_line = self.blanket_so.order_line.filtered(
            lambda l: l.product_id == self.product_1
        )[0]
        self.assertRecordValues(
            order.order_line,
            [
                {
                    "product_uom_qty": 10.0,
                    "price_unit": 0.0,
                    "qty_to_deliver": 10.0,
                    "qty_to_invoice": 0.0,
                    "qty_delivered": 0.0,
                    "display_qty_widget": True,
                    "virtual_available_at_date": blanket_line.virtual_available_at_date,
                    "scheduled_date": blanket_line.scheduled_date,
                    "forecast_expected_date": blanket_line.forecast_expected_date,
                    "free_qty_today": blanket_line.free_qty_today,
                    "qty_available_today": blanket_line.qty_available_today,
                }
            ],
        )
        # once confirmed, the quantity to deliver should become 0 and the
        # display_qty_widget should be False
        with freezegun.freeze_time("2025-02-01"):
            order.action_confirm()
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
                }
            ],
        )


@freezegun.freeze_time("2025-02-01")
class TestSaleCallOffOrderProcessing(SaleOrderBlanketOrderCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blanket_so.action_confirm()

    def test_processing(self):
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
            self.assertEqual(line.blanket_line_id, sale_line)

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

        # part of the quantity into the blanket order are now delivered
        blanket_lines = self.blanket_so.order_line.filtered(
            lambda l: l.product_id == self.product_1
        )
        self.assertEqual(len(blanket_lines), 2)
        self.assertEqual(
            sum(blanket_lines.mapped("qty_delivered")),
            15.0,
        )

        # the call-off order line has been split into 2 lines, each one linked to
        # a different blanket order line
        self.assertEqual(len(order.order_line), 2)
        self.assertEqual(
            order.order_line.blanket_line_id,
            blanket_lines,
        )


@freezegun.freeze_time("2025-02-01")
class TestSaleAutoDoneCallOffOrderProcessing(TestSaleCallOffOrderProcessing):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("sale.group_auto_done_setting")

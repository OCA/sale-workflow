# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import freezegun

from odoo import Command
from odoo.tests.common import RecordCapturer

from .common import SaleOrderBlanketOrderCase


class TestSaleNormalOrder(SaleOrderBlanketOrderCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blanket_so.action_confirm()

    @classmethod
    def _set_cut_off_auto_create_mode(cls, value):
        # Enable the auto create mode
        cls.env["res.config.settings"].create(
            {"create_call_off_from_so_if_possible": True}
        ).execute()

    @freezegun.freeze_time("2025-02-01")
    def test_normal_order(self):
        # ensure that the original sale order process
        # works as expected
        # We use product_3 since it is not part of a blanket order
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_3.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        order.action_confirm()

    @freezegun.freeze_time("2025-02-01")
    def test_call_off_auto_create_mode(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        with RecordCapturer(self.so_model, self.call_off_domain) as captured:
            order.action_confirm()
        new_order = captured.records
        # By default the auto create mode is disabled
        self.assertEqual(len(new_order), 0)

        # Enable the auto create mode
        self._set_cut_off_auto_create_mode(True)
        order.action_draft()
        with RecordCapturer(self.so_model, self.call_off_domain) as captured:
            order.action_confirm()
        new_order = captured.records
        self.assertEqual(len(new_order), 1)
        self.assertEqual(new_order.partner_id, order.partner_id)
        self.assertEqual(new_order.state, "sale")
        self.assertEqual(new_order.order_type, "call_off")
        self.assertEqual(new_order.blanket_order_id, self.blanket_so)

    @freezegun.freeze_time("2025-02-01")
    def test_call_off_auto_create(self):
        # A test where we've a SO with 2 products,
        # one of which is part of a blanket order
        # and the other is not
        # The quantity of the product that is part of the blanket order
        # is less than the quantity in the blanket order
        self._set_cut_off_auto_create_mode(True)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": self.product_3.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )
        with RecordCapturer(self.so_model, self.call_off_domain) as captured:
            order.action_confirm()
        new_order = captured.records
        self.assertEqual(len(new_order), 1)
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.product_id, self.product_3)
        self.assertEqual(len(new_order.order_line), 1)
        self.assertEqual(new_order.order_line.product_id, self.product_1)
        self.assertEqual(new_order.order_line.product_uom_qty, 1)
        blanket_lines = self.blanket_so.order_line.filtered(
            lambda x: x.product_id == self.product_1
        )
        blanquet_product_qty = sum(blanket_lines.mapped("product_uom_qty"))
        remaining_qty = sum(blanket_lines.mapped("call_off_remaining_qty"))
        self.assertEqual(blanquet_product_qty, remaining_qty + 1)

    @freezegun.freeze_time("2025-02-01")
    def test_call_off_auto_create_qty_multi_blanket_line(self):
        # A test where we've a SO with 1 product for which we have 2 blanket lines
        # The quantity of the product that is part of the normal order is less
        # than the total quantity in the blanket order lines but greater than the
        # quantity in each line.
        # The system should create a call off order with 2 lines for the same product
        # where each line corresponds to a blanket line and one of the lines
        # fulfills the remaining quantity of the first blanket line.
        # product_1 is part of the blanket order with 2 lines each with a quantity
        # of 10
        self._set_cut_off_auto_create_mode(True)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 15,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )
        with RecordCapturer(self.so_model, self.call_off_domain) as captured:
            order.action_confirm()
        new_order = captured.records
        self.assertEqual(len(new_order), 1)
        self.assertEqual(
            len(order.order_line), 0
        )  # All lines are moved to the call off order
        self.assertEqual(len(new_order.order_line), 2)
        blanket_lines = self.blanket_so.order_line.filtered(
            lambda x: x.product_id == self.product_1
        )
        blanquet_product_qty = sum(blanket_lines.mapped("product_uom_qty"))
        remaining_qty = sum(blanket_lines.mapped("call_off_remaining_qty"))
        self.assertEqual(blanquet_product_qty, remaining_qty + 15)

    @freezegun.freeze_time("2025-02-01")
    def test_call_off_auto_create_qty_multi_blanket_line_overflow(self):
        # A test where we've a SO with 1 product for which we have 2 blanket lines
        # The quantity of the product that is part of the normal order is greater
        # than the total quantity in the blanket order lines.
        # The system should create a call off order with 2 lines for the same product
        # where each line corresponds to a blanket line and fulfill the quantity
        # of the blanket lines. The original order should have one line with the
        # remaining quantity.
        # product_1 is part of the blanket order with 2 lines each with a quantity
        # of 10
        self._set_cut_off_auto_create_mode(True)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 25,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )
        with RecordCapturer(self.so_model, self.call_off_domain) as captured:
            order.action_confirm()
        new_order = captured.records
        self.assertEqual(len(new_order), 1)
        self.assertEqual(
            len(order.order_line), 1
        )  # All lines are moved to the call off order
        self.assertEqual(len(new_order.order_line), 2)
        blanket_lines = self.blanket_so.order_line.filtered(
            lambda x: x.product_id == self.product_1
        )
        remaining_qty = sum(blanket_lines.mapped("call_off_remaining_qty"))
        self.assertEqual(remaining_qty, 0)
        self.assertEqual(order.order_line.product_uom_qty, 5)

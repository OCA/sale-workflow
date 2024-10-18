# Copyright 2024 Akretion - Olivier Nibart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from .common import TestCommon


class TestSaleOrderPrimeship(TestCommon):
    def test_action_confirm_creates_primeship(self):
        order_line = self.make_order_line()
        self.order.action_confirm()

        self.assertTrue(order_line.primeship_id)
        self.assertEqual(order_line.primeship_id.partner_id, self.partner)
        self.assertEqual(order_line.primeship_id.order_line_id, order_line)
        self.assertEqual(order_line.primeship_id.start_date, date.today())
        self.assertEqual(
            order_line.primeship_id.end_date,
            order_line.primeship_id.start_date + relativedelta(months=6),
        )

    def test_action_confirm_extends_existing_primeship(self):
        existing_primeship = self.make_primeship(
            date.today() - relativedelta(months=3),
            date.today() + relativedelta(months=3),
        )
        order_line = self.make_order_line()
        self.order.action_confirm()

        self.assertEqual(
            order_line.primeship_id.start_date, existing_primeship.end_date
        )
        self.assertEqual(
            order_line.primeship_id.end_date,
            order_line.primeship_id.start_date + relativedelta(months=6),
        )

    def test_action_cancel_deactivates_primeship(self):
        order_line = self.make_order_line()
        self.order.action_confirm()
        original_primeship = order_line.primeship_id
        self.assertTrue(original_primeship.active)

        self.order.action_cancel()
        self.assertFalse(original_primeship.active)

    def test_action_confirm_with_existing_primeship(self):
        order_line = self.make_order_line()
        self.order.action_confirm()
        original_primeship = order_line.primeship_id
        self.order.action_cancel()

        # recomputing the primeship_id will detach
        # the deactivated primeship from the order line
        order_line._compute_primeship_id()
        self.assertFalse(order_line.primeship_id)

        self.order.action_draft()
        self.assertFalse(original_primeship.active)

        # we should now retrieve the deactivated primeship
        # and reactivate it
        self.order.action_confirm()
        self.assertTrue(order_line.primeship_id.active)
        self.assertEqual(order_line.primeship_id.id, original_primeship.id)

        self.order.action_cancel()

        # we do not recompute the primeship_id so even though it is
        # deactivated, order_line.primeship_id is still pointing at it
        self.assertEqual(order_line.primeship_id.id, original_primeship.id)

        self.order.action_draft()

        # we should now use the still attached deactivated primeship
        # and reactivate it
        self.order.action_confirm()
        self.assertTrue(original_primeship.active)
        self.assertEqual(order_line.primeship_id.id, original_primeship.id)

    def test_prepare_invoice_line_with_primeship(self):
        order_line = self.make_order_line()
        self.order.action_confirm()

        invoice_line_vals = order_line._prepare_invoice_line()
        self.assertEqual(
            invoice_line_vals["start_date"], order_line.primeship_id.start_date
        )
        self.assertEqual(
            invoice_line_vals["end_date"], order_line.primeship_id.end_date
        )

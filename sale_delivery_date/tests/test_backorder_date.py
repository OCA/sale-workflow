# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time

from odoo.tests.common import Form

from .common import Common

MONDAY = "2022-04-11"
THURSDAY = "2022-04-14"
FRIDAY = "2022-04-15"
# The week after
NEXT_THURSDAY = "2022-04-21"
NEXT_FRIDAY = "2022-04-22"
# As per Common config, those hours are in "UTC" TZ
BEFORE_CUTOFF_UTC = "06:00:00"
CUTOFF_UTC = "07:00:00"
AFTER_CUTOFF_UTC = "08:00:00"
TIME_WINDOW_START_UTC = "06:00:00"
WAREHOUSE_START_UTC = "07:00:00"
MONDAY_BEFORE_CUTOFF_UTC = f"{MONDAY} {BEFORE_CUTOFF_UTC}"


@freeze_time(MONDAY_BEFORE_CUTOFF_UTC)
class TestBackorderDate(Common):
    # Two cases to ensure here:
    #   - If a backorder is created, then its delivery dates are postponed
    #   - If we modify a SO (I.E. add lines) after it has been confirmed,
    #     the delivery date of the picking might be reevaluated
    # Configuration:
    #   - partner_cutoff: 07:00:00 UTC
    #   - wh calendar: start=07:00:00 UTC, end=15:00:00 UTC
    #   - partner window: between 06:00:00 UTC and 16:00:00 UTC on fridays
    # With this config, an a SO confirmed on, 2022-04-11 (monday) at 06:00:00 UTC,
    # the first picking should have the following dates:
    #   - date_deadline: 2022-04-15 06:00
    #   - scheduled_date: 2022-04-14 07:00:00

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set customer's time window to friday, so delivery is postponed by 1
        # week, which makes it easier to test
        cls._set_partner_time_window_to_friday(cls.customer_partner_cutoff)

    @classmethod
    def _get_default_products(cls):
        # Change the qty from 1 to 10
        return [(cls.product, 10)]

    def _create_and_confirm_order(self):
        order = self._create_order_partner_cutoff()
        order.action_confirm()
        # Here, we want to ensure that the picking date is correctly postponed
        order.picking_ids.move_type = "one"
        return order

    def _create_backorder(self):
        order = self._create_and_confirm_order()
        picking = order.picking_ids
        # Set the half as done, then confirm the picking
        picking.move_lines.quantity_done = 5.0
        picking._action_done()
        return order.picking_ids - picking

    def _increase_so_line_qty(self, qty):
        order = self._create_and_confirm_order()
        with Form(order) as so:
            with so.order_line.edit(0) as line:
                line.product_uom_qty += qty
        return order

    def test_backorder_before_scheduled_date(self):
        # If we want the backorder to be delivered this week, then it has to be
        # created before monday's cutoff.
        # If so, it will be delivered friday, at 06:00
        with freeze_time(f"{THURSDAY} {BEFORE_CUTOFF_UTC}"):
            backorder = self._create_backorder()
        self.assertEqual(str(backorder.scheduled_date), f"{THURSDAY} {CUTOFF_UTC}")
        self.assertEqual(
            str(backorder.date_deadline), f"{FRIDAY} {WAREHOUSE_START_UTC}"
        )

    def test_backorder_after_scheduled_date(self):
        # If we want the backorder to be delivered this week, then it has to be
        # created before monday's cutoff.
        # If so, it will be delivered friday, at 06:00
        with freeze_time(f"{THURSDAY} {AFTER_CUTOFF_UTC}"):
            backorder = self._create_backorder()
        self.assertEqual(str(backorder.scheduled_date), f"{NEXT_THURSDAY} {CUTOFF_UTC}")
        self.assertEqual(
            str(backorder.date_deadline), f"{NEXT_FRIDAY} {WAREHOUSE_START_UTC}"
        )

    def test_increased_qty_before_scheduled_date(self):
        # If we increase a qty of a confirmed SO before the related picking's
        # scheduled_date, nothing should be updated
        with freeze_time(f"{THURSDAY} {BEFORE_CUTOFF_UTC}"):
            order = self._increase_so_line_qty(5)
        # Just ensure that the qty is updated on the stock move
        self.assertEqual(
            sum(order.picking_ids.move_lines.mapped("product_uom_qty")), 15
        )
        self.assertEqual(
            str(order.picking_ids.scheduled_date), f"{THURSDAY} {CUTOFF_UTC}"
        )
        self.assertEqual(
            str(order.picking_ids.date_deadline), f"{FRIDAY} {WAREHOUSE_START_UTC}"
        )

    def test_increased_qty_after_scheduled_date(self):
        # If we increase a qty of a confirmed SO after the related picking's
        # scheduled_date, then the dates should be updated accordingly
        with freeze_time(f"{THURSDAY} {AFTER_CUTOFF_UTC}"):
            order = self._increase_so_line_qty(5)
        # Just ensure that the qty is updated on the stock move
        self.assertEqual(
            sum(order.picking_ids.move_lines.mapped("product_uom_qty")), 15
        )
        # Dates should have been postponed to next week
        self.assertEqual(
            str(order.picking_ids.scheduled_date), f"{NEXT_THURSDAY} {CUTOFF_UTC}"
        )
        self.assertEqual(
            str(order.picking_ids.date_deadline),
            f"{NEXT_FRIDAY} {WAREHOUSE_START_UTC}",
        )

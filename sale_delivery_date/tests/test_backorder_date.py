# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time

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
        cls.order = cls.order_partner_cutoff
        cls.order.action_confirm()
        cls.picking = cls.order.picking_ids
        # Here, we want to ensure that the picking date is correctly postponed
        cls.picking.move_type = "one"

    @classmethod
    def _get_default_products(cls):
        return [(cls.product, 10)]

    @classmethod
    def _create_backorder(cls):
        # Set the half as done, then confirm the picking
        cls.picking.move_lines.quantity_done = 5.0
        cls.picking._action_done()
        return cls.order.picking_ids - cls.picking

    def test_backorder_before_scheduled_date(self):
        # If we want the backorder to be delivered this week, then it has to be
        # created before monday's cutoff.
        # If so, it will be delivered friday, at 06:00
        with freeze_time(f"{THURSDAY} {BEFORE_CUTOFF_UTC}"):
            backorder = self._create_backorder()
        self.assertEqual(str(backorder.scheduled_date), f"{THURSDAY} {CUTOFF_UTC}")
        self.assertEqual(
            str(backorder.date_deadline), f"{FRIDAY} {TIME_WINDOW_START_UTC}"
        )

    def test_backorder_after_scheduled_date(self):
        # If we want the backorder to be delivered this week, then it has to be
        # created before monday's cutoff.
        # If so, it will be delivered friday, at 06:00
        with freeze_time(f"{THURSDAY} {AFTER_CUTOFF_UTC}"):
            backorder = self._create_backorder()
        self.assertEqual(str(backorder.scheduled_date), f"{NEXT_THURSDAY} {CUTOFF_UTC}")
        self.assertEqual(
            str(backorder.date_deadline), f"{NEXT_FRIDAY} {TIME_WINDOW_START_UTC}"
        )

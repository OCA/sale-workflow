# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time
from datetime import timedelta

from .common import Common

BEFORE_CUTOFF = "07:30:00"
AFTER_CUTOFF = "08:30:00"
THURSDAY = "2021-08-19"
FRIDAY = "2021-08-20"
SATURDAY = "2021-08-21"
SUNDAY = "2021-08-22"
NEXT_MONDAY = "2021-08-23"
NEXT_TUESDAY = "2021-08-24"
NEXT_WEDNESDAY = "2021-08-25"
NEXT_THURSDAY = "2021-08-26"
NEXT_FRIDAY = "2021-08-27"
# NOTE: the following dates are UTC, with 'Europe/Paris' we are GMT+2
THURSDAY_BEFORE_CUTOFF = f"{THURSDAY} {BEFORE_CUTOFF}"
THURSDAY_AFTER_CUTOFF = f"{THURSDAY} {AFTER_CUTOFF}"
FRIDAY_BEFORE_CUTOFF = f"{FRIDAY} {BEFORE_CUTOFF}"
FRIDAY_AFTER_CUTOFF = f"{FRIDAY} {AFTER_CUTOFF}"


class TestSaleDeliveryDate(Common):
    @classmethod
    def setUpClassPartner(cls):
        super().setUpClassPartner()
        cls.customer_warehouse_cutoff.delivery_time_preference = "workdays"

    @freeze_time(THURSDAY_AFTER_CUTOFF)
    def test_order_on_thursday_after_cutoff_to_deliver_on_workdays(self):
        """Order confirmed after cut-off time on Thursday to deliver on workdays."""
        # next cutoff friday @ 7:00
        # next end work friday @ 15:00
        # + security_lead saturday @ 15:00
        # next window = monday @ 15:00
        #
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), FRIDAY)
        # self.assertEqual(str(picking.date_deadline.date()), FRIDAY)
        self.assertEqual(str(order.expected_date.date()), NEXT_MONDAY)

    @freeze_time(THURSDAY_BEFORE_CUTOFF)
    def test_order_on_thursday_before_cutoff_to_deliver_on_workdays(self):
        """Order confirmed before cut-off time on Thursday to deliver on workdays."""
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), THURSDAY)
        self.assertEqual(str(order.expected_date.date()), FRIDAY)

    @freeze_time(FRIDAY_AFTER_CUTOFF)
    def test_order_on_friday_after_cutoff_to_deliver_on_workdays(self):
        """Order confirmed after cut-off time on Friday to deliver on workdays."""
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(order.expected_date.date()), NEXT_TUESDAY)
        self.assertEqual(str(picking.scheduled_date.date()), NEXT_MONDAY)

    @freeze_time(FRIDAY_BEFORE_CUTOFF)
    def test_order_on_friday_before_cutoff_to_deliver_on_workdays(self):
        """Order confirmed before cut-off time on Friday to deliver on workdays."""
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), FRIDAY)
        self.assertEqual(str(order.expected_date.date()), NEXT_MONDAY)

    @freeze_time(FRIDAY_AFTER_CUTOFF)
    def test_order_on_friday_after_cutoff_to_deliver_on_friday(self):
        """Order confirmed after cut-off time on Friday to deliver on friday."""
        # now = 2021-08-20 08:30:00
        # Apply cutoff : 2021-08-21 08:00:00
        # next_working_day: 2021-08-23 08:00:00
        # apply workload: 2021-08-23 17:00:00
        # apply security_lead: 2021-08-24 00:00:00
        # apply time window: 2021-08-27 08:00:00 (delivery_date)
        # ====
        # deduct security_lead: 2021-08-26 23:59:59 (TODO should be time.maxed)
        # previous end attendance: 2021-08-26 17:00:00
        # latest start work: 2021-08-26 08:00:00
        weekday_numbers = (4,)  # friday from 8 to 18
        time_window_ranges = [
            (8.0, 18.0)
        ]
        self._set_partner_time_window(
            self.customer_warehouse_cutoff, weekday_numbers, time_window_ranges
        )
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), NEXT_THURSDAY)
        self.assertEqual(str(order.expected_date.date()), NEXT_FRIDAY)

    @freeze_time(FRIDAY_BEFORE_CUTOFF)
    def test_order_on_friday_before_cutoff_to_deliver_on_friday(self):
        """Order confirmed before cut-off time on Friday to deliver on friday."""
        weekday_numbers = (4,)  # friday from 8 to 18
        time_window_ranges = [
            (8.0, 18.0)
        ]
        self._set_partner_time_window(
            self.customer_warehouse_cutoff, weekday_numbers, time_window_ranges
        )
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), NEXT_THURSDAY)
        self.assertEqual(str(order.expected_date.date()), NEXT_FRIDAY)

    @freeze_time("2023-06-06 07:55:00")
    def test_order_on_monday_before_cutoff_with_leaves(self):
        expected_work_start_date = "2023-06-06"
        expected_delivery_date = "2023-06-09"
        self._set_partner_time_window_working_days(self.customer_warehouse_cutoff)
        self._add_calendar_leaves(self.calendar, ["2023-06-07", "2023-06-08"])
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), expected_work_start_date)
        self.assertEqual(str(order.expected_date.date()), expected_delivery_date)

    @freeze_time("2023-06-20 15:19:31")
    def test_order_on_tuesday_after_cutoff(self):
        # Set calendar attendances on weekdays, from 8 to 12, 13 to 17.5
        weekday_numbers = tuple(range(5))
        time_ranges = [(8.0, 12.0), (13.0, 17.5)]
        self._set_calendar_attendances(self.calendar, weekday_numbers, time_ranges)
        expected_work_start_date = "2023-06-21"
        expected_delivery_date = "2023-06-22"  # weekdays from 6 to 8
        weekday_numbers = tuple(range(5))
        time_window_ranges = [
            (6.5, 8.02),
        ]
        self._set_partner_time_window(
            self.customer_warehouse_cutoff, weekday_numbers, time_window_ranges
        )
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), expected_work_start_date)
        self.assertEqual(str(order.expected_date.date()), expected_delivery_date)

    @freeze_time("2023-07-06 15:00:00")
    def test_order_after_cutoff_to_delivery_tomorrow(self):
        # Let's say we can ask a guy in the warehouse to work on this order
        # right now to be ready to deliver today.
        # With a commitment_date we can do that
        weekday_numbers = tuple(range(5))
        time_ranges = [(8.0, 12.0), (13.0, 17.5)]
        self._set_calendar_attendances(self.calendar, weekday_numbers, time_ranges)
        weekday_numbers = tuple(range(5))
        # Working days, from 7:30 to 12:00 then from 13:00 to 15:30
        time_window_ranges = [(7.5, 12.0), (13.0, 15.5), ]
        self._set_partner_time_window(
            self.customer_warehouse_cutoff, weekday_numbers, time_window_ranges
        )
        order = self.order_warehouse_cutoff
        order.commitment_date = "2023-07-07 16:00:00"
        expected_work_start_date = "2023-07-06 08:00:00" # 10:00 UTC
        expected_delivery_date = "2023-07-07 05:30:00" # 07:30 UTC
        order.action_confirm()
        picking = order.picking_ids
        # If the employee can process the order now an give the goods to the
        # carrier today, then goods can be received tomorrow at commitment_date.
        self.assertEqual(str(picking.scheduled_date), expected_work_start_date)
        self.assertEqual(str(picking.expected_delivery_date), "2023-07-07 16:00:00")

    @freeze_time("2023-07-06 15:00:00") # 15:00 UTC is 17:00 Europe/Brussels
    def test_order_on_thursday_after_cutoff_late_commitment_date(self):
        # Following the above case, this can is impossible to achieve,
        # because the commitment_date will be in the past from the begining
        order = self.order_warehouse_cutoff
        order.commitment_date = "2023-07-05 15:00:00"
        # Warehouse working from 8:00 to 12:00 and 13:00 to 17:30 on working days
        weekday_numbers = tuple(range(5))
        time_ranges = [(8.0, 12.0), (13.0, 17.5)]
        self._set_calendar_attendances(self.calendar, weekday_numbers, time_ranges)
        # Customer working from, from 7:30 to 12:00 then from 13:00 to 15:30
        weekday_numbers = tuple(range(5))
        time_window_ranges = [(7.5, 12.0), (13.0, 15.5)]
        self._set_partner_time_window(
            self.customer_warehouse_cutoff, weekday_numbers, time_window_ranges
        )
        # When we confirm, we're already late to deliver, but the date_deadline
        # is still matching the commitment_date
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.date_deadline), "2023-07-05 15:00:00")
        # The scheduled date is the start of the previous attendance.
        # This is when we should have started working on this.
        self.assertEqual(str(picking.scheduled_date), "2023-07-04 08:00:00") # 10:00 UTC
        # date_deadline is immutable.
        # However, there might be cases where you cannot use a date in the past,
        # a carrier for instance, whose API would refuse any date in the past.
        # For such cases, we can use picking.expected_delivery_date, which represents
        # the next open day.
        # This date doesn't take into account the customer delivery preferences.
        # On 2023-07-06 16:00:00, best delivery date is the day after.
        self.assertEqual(
            str(picking.expected_delivery_date.date()), "2023-07-07"
        )

    @freeze_time("2023-08-18 13:05:50") # 15:05:50 Europe/Brussels
    def test_friday_order_with_commitment_date(self):
        order = self.order_warehouse_cutoff
        commitment_date = "2023-08-23"
        order.commitment_date = commitment_date
        # WH open from mon to fri, from 8 to 12, then from 13 to 17:30
        weekday_numbers = tuple(range(5))
        time_ranges = [(8.0, 12.0), (13.0, 17.5)]
        self._set_calendar_attendances(self.calendar, weekday_numbers, time_ranges)
        # Customer receiving goods from 8 to 11 on thursdays
        weekday_numbers = [3, ]
        time_window_ranges = [(8, 11), ]
        self._set_partner_time_window(
            self.customer_warehouse_cutoff, weekday_numbers, time_window_ranges
        )
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date), "2023-08-22 08:00:00")
        self.assertEqual(str(picking.date_deadline.date()), "2023-08-23")
        self.assertEqual(str(picking.expected_delivery_date.date()), "2023-08-23")
        # Also, picking.expected_delivery_date should display the same.
        # scheduled_date = "expedition date"
        # As expected_delivery_date is computed and based on the time it is generated
        # we have to set current time as after the scheduled date, hence the
        # timedelta
        with freeze_time(str(picking.scheduled_date + timedelta(hours=1))):
            self.assertEqual(str(picking.date_deadline.date()), "2023-08-23")
            self.assertEqual(str(picking.expected_delivery_date.date()), "2023-08-23")
        # Now, try to get those dates again, late by 1 day
        picking.invalidate_cache(['expected_delivery_date'])
        with freeze_time(str(picking.scheduled_date + timedelta(days=1))):
            self.assertEqual(str(picking.date_deadline.date()), "2023-08-23")
            self.assertEqual(str(picking.expected_delivery_date.date()), "2023-08-24")

    @freeze_time("2023-08-18 13:05:50")
    def test_friday_order_with_monday_leave(self):
        order = self.order_warehouse_cutoff
        # WH open from mon to fri, from 8 to 12, then from 13 to 17:30
        weekday_numbers = tuple(range(5))
        time_ranges = [(8.0, 12.0), (13.0, 17.5)]
        self._set_calendar_attendances(self.calendar, weekday_numbers, time_ranges)
        # Set customer to receive goods on any day
        self.customer_warehouse_cutoff.delivery_time_preference = "anytime"
        # add a public holiday the 21th of aug
        days = ["2023-08-21", ]
        self._add_calendar_leaves(self.calendar, days)
        order.action_confirm()
        # Order after cutoff, postponed to next open day (tuesday the 22th)
        # And delivered the day after (24th of aug)
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date), "2023-08-22 08:00:00")
        self.assertEqual(str(picking.expected_delivery_date.date()), "2023-08-23")

    @freeze_time("2023-10-09 08:00:00")
    def test_delivery_window_on_public_holiday(self):
        order = self.order_warehouse_cutoff
        weekday_numbers = tuple(range(5))
        time_ranges = [(8.0, 12.0), (13.0, 17.5)]
        self._set_calendar_attendances(self.calendar, weekday_numbers, time_ranges)
        # Set customer to receive goods on Wednesday, from 12 to 17
        weekday_numbers = (2,)  # Wednesday
        time_window_ranges = [(12.00, 17.00), ]
        self._set_partner_time_window(
            self.customer_warehouse_cutoff, weekday_numbers, time_window_ranges
        )
        # add a public holiday the 11th of October
        days = ["2023-10-11", ]
        self._add_calendar_leaves(self.calendar, days)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), "2023-10-17")
        self.assertEqual(str(picking.date_deadline.date()), "2023-10-18")

    @freeze_time("2023-10-09 08:00:00")
    def test_no_open_delivery_window_within_twenty_days(self):
        order = self.order_warehouse_cutoff
        weekday_numbers = tuple(range(5))
        time_ranges = [(8.0, 12.0), (13.0, 17.5)]
        self._set_calendar_attendances(self.calendar, weekday_numbers, time_ranges)
        # Set customer to receive goods on Wednesday, from 12 to 17
        weekday_numbers = (2,)  # Wednesday
        time_window_ranges = [(12.00, 17.00), ]
        self._set_partner_time_window(
            self.customer_warehouse_cutoff, weekday_numbers, time_window_ranges
        )
        # add a public holiday all fridays
        days = [
            "2023-10-11",
            "2023-10-18",
            "2023-10-25",
            "2023-11-01",
        ]
        self._add_calendar_leaves(self.calendar, days)
        logger_name = "odoo.addons.sale_delivery_date.models.sale_order_line"
        with self.assertLogs(logger_name, level="WARNING") as watcher:
            line = order.order_line
            order.action_confirm()
            expected_message = (
                f"WARNING:{logger_name}:"
                f"Unable to find a valid delivery date for line {line.name}. "
                f"Falling back to 2023-10-11."
            )
            self.assertEqual(watcher.output[0], expected_message)
        picking = order.picking_ids
        # since we weren't able to find an open friday within 20 days,
        # we fell back on the first one, being the 11th of october
        self.assertEqual(str(picking.scheduled_date.date()), "2023-10-10")
        self.assertEqual(str(picking.date_deadline.date()), "2023-10-11")

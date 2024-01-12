# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time
from datetime import datetime, timedelta

from odoo.tests.common import Form
from odoo.tools import mute_logger

from .common import Common


class TestMethods(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_line_model = cls.env["sale.order.line"]
        cls.order = cls.order_warehouse_cutoff
        cls.order_line = cls.order.order_line
        cls.partner = cls.order.partner_id
        cls.warehouse.tz = "UTC"
        cls.calendar.tz = "UTC"
        cls.partner.tz = "UTC"

    @classmethod
    def _set_wh_tz(cls, tz_string):
        cls.warehouse.tz = tz_string

    @classmethod
    def _set_calendar_tz(cls, tz_string):
        cls.calendar.tz = tz_string

    @classmethod
    def _set_customer_tz(cls, tz_string):
        cls.partner.tz = tz_string

    @classmethod
    def _no_cutoff(cls):
        cls.customers.write({"cutoff_time": False})
        cls.warehouse.write({"apply_cutoff": False})

    @classmethod
    def _no_calendar(cls):
        cls.warehouse.calendar2_id = False

    @classmethod
    def _set_delivery_time_preference(cls, partner, delivery_time_preference):
        if delivery_time_preference == "time_windows":
            # fridays from 8 to 18
            weekday_numbers = (4,)
            time_window_ranges = [(8.0, 18.0)]
            cls._set_partner_time_window(partner, weekday_numbers, time_window_ranges)
            return
        partner.delivery_time_preference = delivery_time_preference

    # sale.order.line._deduct_delay

    def test_deduct_delay_no_calendar(self):
        # With no calendar set, retrieves N days with timedelta
        self._no_calendar()
        from_date = datetime(2023, 4, 11, 17, 0)
        res = self.order_line._deduct_delay(from_date, 1)
        self.assertEqual(str(res), "2023-04-10 17:00:00")
        res = self.order_line._deduct_delay(from_date, 5)
        self.assertEqual(str(res), "2023-04-06 17:00:00")

    def test_deduct_delay_with_calendar(self):
        from_date = datetime(2023, 4, 11, 17, 0)
        res = self.order_line._deduct_delay(from_date, 1, calendar=self.calendar)
        self.assertEqual(str(res), "2023-04-10 09:00:00")
        res = self.order_line._deduct_delay(from_date, 5, calendar=self.calendar)
        self.assertEqual(str(res), "2023-04-04 09:00:00")
        # with the `use_calendar` argument set to false, we should have the
        # same results as in `test_deduct_delay_no_calendar`
        res = self.order_line._deduct_delay(from_date, 1)
        self.assertEqual(str(res), "2023-04-10 17:00:00")
        res = self.order_line._deduct_delay(from_date, 5)
        self.assertEqual(str(res), "2023-04-06 17:00:00")

    # sale.order.line._add_delay

    def test_add_delay_no_calendar(self):
        # With no calendar set, adds N days with timedelta
        self._no_calendar()
        from_date = datetime(2023, 4, 11, 12)
        res = self.order_line._add_delay(from_date, 1)
        self.assertEqual(str(res), "2023-04-12 12:00:00")
        res = self.order_line._add_delay(from_date, 5)
        self.assertEqual(str(res), "2023-04-16 12:00:00")

    def test_add_delay_with_calendar(self):
        # 2023-04-12 12:00:00 is a tuesday
        from_date = datetime(2023, 4, 11, 12)
        # Here, what's important to understand is that a delay of 0 means
        # that we will be able to process the order within the day
        # A delay of 1 means that the order will be processed by tomorrow at the
        # the end of the attendance, and so on.
        res = self.order_line._add_delay(from_date, 1, calendar=self.calendar)
        self.assertEqual(str(res), "2023-04-12 17:00:00")
        res = self.order_line._add_delay(from_date, 5, calendar=self.calendar)
        self.assertEqual(str(res), "2023-04-18 17:00:00")
        # with the `use_calendar` argument set to false, we should have the
        # same results as in `test_add_delay_no_calendar`
        res = self.order_line._add_delay(from_date, 1)
        self.assertEqual(str(res), "2023-04-12 12:00:00")
        res = self.order_line._add_delay(from_date, 5)
        self.assertEqual(str(res), "2023-04-16 12:00:00")

    def test_add_delay_with_calendar_with_tz(self):
        self._set_calendar_tz("Europe/Paris")
        # 2023-04-12 12:00:00 is a tuesday
        from_date = datetime(2023, 4, 11, 12)
        # Here, what's important to understand is that a delay of 0 means
        # that we will be able to process the order within the day
        # A delay of 1 means that the order will be processed by tomorrow at the
        # the end of the attendance, and so on.
        res = self.order_line._add_delay(from_date, 1, calendar=self.calendar)
        self.assertEqual(str(res), "2023-04-12 15:00:00")
        res = self.order_line._add_delay(from_date, 5, calendar=self.calendar)
        self.assertEqual(str(res), "2023-04-18 15:00:00")
        # with the `use_calendar` argument set to false, we should have the
        # same results as in `test_add_delay_no_calendar`
        res = self.order_line._add_delay(from_date, 1)
        self.assertEqual(str(res), "2023-04-12 12:00:00")
        res = self.order_line._add_delay(from_date, 5)
        self.assertEqual(str(res), "2023-04-16 12:00:00")

    # sale.order.line._apply_cutoff

    def test_apply_cutoff_without_cutoff(self):
        self._no_cutoff()
        # In such case, input dates shouldn't be altered
        # WH cutoff is 10:00
        cutoff = {}
        before_cutoff_datetime = datetime(2023, 4, 11, 9, 59, 59)
        res = self.order_line._apply_cutoff(before_cutoff_datetime, cutoff)
        self.assertEqual(before_cutoff_datetime, res)
        after_cutoff_datetime = datetime(2023, 4, 11, 10, 0, 1)
        res = self.order_line._apply_cutoff(after_cutoff_datetime, cutoff)
        self.assertEqual(after_cutoff_datetime, res)

    def test_apply_cutoff(self):
        before_cutoff_datetime = datetime(2023, 4, 11, 9, 59, 59)
        cutoff = self.order.get_cutoff_time()
        res = self.order_line._apply_cutoff(before_cutoff_datetime, cutoff)
        self.assertEqual(str(res), "2023-04-11 10:00:00")
        after_cutoff_datetime = datetime(2023, 4, 11, 10, 0, 1)
        res = self.order_line._apply_cutoff(after_cutoff_datetime, cutoff)
        self.assertEqual(str(res), "2023-04-12 10:00:00")
        # With keep_same_day, only time is changed to cutoff
        res = self.order_line._apply_cutoff(
            before_cutoff_datetime, cutoff, keep_same_day=True
        )
        self.assertEqual(str(res), "2023-04-11 10:00:00")
        res = self.order_line._apply_cutoff(
            after_cutoff_datetime, cutoff, keep_same_day=True
        )
        self.assertEqual(str(res), "2023-04-11 10:00:00")

    def test_apply_cutoff_with_tz(self):
        tz = "Europe/Paris"
        self._set_wh_tz(tz)
        cutoff = self.order.get_cutoff_time()
        self.assertEqual(cutoff.get("tz"), tz)
        # with Europe/Paris 10:00 as a cutoff, UTC cutoff is 08:00
        before_cutoff_datetime = datetime(2023, 4, 11, 7, 59, 59)
        res = self.order_line._apply_cutoff(before_cutoff_datetime, cutoff)
        self.assertEqual(str(res), "2023-04-11 08:00:00")
        after_cutoff_datetime = datetime(2023, 4, 11, 8, 0, 1)
        res = self.order_line._apply_cutoff(after_cutoff_datetime, cutoff)
        self.assertEqual(str(res), "2023-04-12 08:00:00")
        # With keep_same_day, only time is changed to cutoff
        res = self.order_line._apply_cutoff(
            before_cutoff_datetime, cutoff, keep_same_day=True
        )
        self.assertEqual(str(res), "2023-04-11 08:00:00")
        res = self.order_line._apply_cutoff(
            after_cutoff_datetime, cutoff, keep_same_day=True
        )
        self.assertEqual(str(res), "2023-04-11 08:00:00")

    # sale.order.line._postpone_to_working_day

    def test_postpone_to_working_day_no_calendar(self):
        # In such case, input dates shouldn't be altered
        monday_before_cutoff = datetime(2023, 4, 10, 9, 59, 59)
        res = self.order_line._postpone_to_working_day(monday_before_cutoff)
        self.assertEqual(res, monday_before_cutoff)
        sunday = datetime(2023, 4, 9, 10, 0, 0)
        res = self.order_line._postpone_to_working_day(sunday)
        self.assertEqual(res, sunday)

    def test_postpone_to_working_day_with_calendar(self):
        # Dates should be postponed to the start of the next attendance if
        # not inside of one. Otherwise, it should return the input date
        monday_before_start = datetime(2023, 4, 10, 8, 59, 59)
        monday_during_attendance = datetime(2023, 4, 10, 12, 0, 0)
        monday_after_end = datetime(2023, 4, 10, 17, 0, 1)
        monday_start = datetime(2023, 4, 10, 9, 0, 0)
        tuesday_start = datetime(2023, 4, 11, 9, 0, 0)
        sunday = datetime(2023, 4, 9, 10, 0, 0)
        # monday 08:59:59 is before monday's attendance, postpone it to monday 09:00
        res = self.order_line._postpone_to_working_day(
            monday_before_start, calendar=self.calendar
        )
        self.assertEqual(res, monday_start)
        # sunday isn't a working day, postpone it to monday 9:00
        res = self.order_line._postpone_to_working_day(sunday, calendar=self.calendar)
        self.assertEqual(res, monday_start)
        # monday 17:00:01 is after monday's attendance, postpone it to tuesday 09:00
        res = self.order_line._postpone_to_working_day(
            monday_after_end, calendar=self.calendar
        )
        self.assertEqual(res, tuesday_start)
        # monday 12:00:00 is in monday's attendance, keep it as it is
        res = self.order_line._postpone_to_working_day(
            monday_during_attendance, calendar=self.calendar
        )
        self.assertEqual(res, monday_during_attendance)

    def test_postpone_to_working_day_with_calendar_with_tz(self):
        self._set_calendar_tz("Europe/Paris")
        # same tests as test_postpone_to_working_day_with_calendar, but
        # with each expected datetime -2h
        monday_before_start = datetime(2023, 4, 10, 6, 59, 59)
        monday_during_attendance = datetime(2023, 4, 10, 10, 0, 0)
        monday_after_end = datetime(2023, 4, 10, 15, 0, 1)
        monday_start = datetime(2023, 4, 10, 7, 0, 0)
        tuesday_start = datetime(2023, 4, 11, 7, 0, 0)
        sunday = datetime(2023, 4, 9, 8, 0, 0)
        # monday 08:59:59 is before monday's attendance, postpone it to monday 09:00
        res = self.order_line._postpone_to_working_day(
            monday_before_start, calendar=self.calendar
        )
        self.assertEqual(res, monday_start)
        # sunday isn't a working day, postpone it to monday 9:00
        res = self.order_line._postpone_to_working_day(sunday, calendar=self.calendar)
        self.assertEqual(res, monday_start)
        # monday 17:00:01 is after monday's attendance, postpone it to tuesday 09:00
        res = self.order_line._postpone_to_working_day(
            monday_after_end, calendar=self.calendar
        )
        self.assertEqual(res, tuesday_start)
        # monday 12:00:00 is in monday's attendance, keep it as it is
        res = self.order_line._postpone_to_working_day(
            monday_during_attendance, calendar=self.calendar
        )
        self.assertEqual(res, monday_during_attendance)

    def test_apply_customer_window_anytime(self):
        # In this case, input date is returned without any modification, no
        # matter the day of the week
        self._set_delivery_time_preference(self.partner, "anytime")
        for delivery_day in range(10, 17):  # from monday to sunday
            delivery_date = datetime(2023, 4, delivery_day, 12)
            res = self.order_line._apply_customer_window(delivery_date, self.partner)
            self.assertEqual(res, delivery_date)

    def test_apply_customer_window_no_partner(self):
        # If no partner, date is not postponed
        partner = self.env["res.partner"]
        delivery_date = "2023-12-01 00:00:00"
        res = self.order_line._apply_customer_window(delivery_date, partner)
        self.assertEqual(delivery_date, res)

    def test_apply_customer_window_workdays(self):
        # In this case, input date is returned without any modification, no
        # matter the day of the week
        self._set_delivery_time_preference(self.partner, "workdays")
        next_monday = datetime(2023, 4, 17, 12, 0)
        for i in range(10, 17):
            delivery_date = datetime(2023, 4, i, 12)
            res = self.order_line._apply_customer_window(delivery_date, self.partner)
            if delivery_date.weekday() < 5:  # Before saturday
                self.assertEqual(res, delivery_date)
            else:
                # TODO: when postponing to a working day, should we replace
                # hour, minute and second?
                self.assertEqual(res, next_monday)

    def test_apply_customer_window_workdays_with_tz(self):
        # In this case, input date is returned without any modification, no
        # matter the day of the week
        self._set_delivery_time_preference(self.partner, "workdays")
        next_monday = datetime(2023, 4, 17, 12, 0)
        for i in range(10, 17):
            delivery_date = datetime(2023, 4, i, 12)
            res = self.order_line._apply_customer_window(delivery_date, self.partner)
            if delivery_date.weekday() < 5:  # Before saturday
                self.assertEqual(res, delivery_date)
            else:
                # TODO: when postponing to a working day, should we replace
                # hour, minute and second?
                self.assertEqual(res, next_monday)

    def test_apply_customer_window_time_windows(self):
        self._set_delivery_time_preference(self.partner, "time_windows")
        friday_this_week = datetime(2023, 4, 14, 8, 0)
        friday_next_week = datetime(2023, 4, 21, 8, 0)
        for delivery_day in range(10, 17):
            delivery_date = datetime(2023, 4, delivery_day, 12)
            res = self.order_line._apply_customer_window(delivery_date, self.partner)
            if delivery_day < 14:
                # if day is before friday, postpone to saturday this week
                self.assertEqual(res, friday_this_week)
            elif delivery_day == 14:
                # If day is friday (in a time window), keep date as it is
                self.assertEqual(res, delivery_date)
            else:
                # Otherwise, postpone to the next week
                self.assertEqual(res, friday_next_week)

    def test_apply_customer_window_time_windows_with_tz(self):
        self._set_customer_tz("Europe/Paris")
        # With tz set to Europe/Paris, customer's time window start
        # is 6:00 UTC
        self._set_delivery_time_preference(self.partner, "time_windows")
        friday_this_week = datetime(2023, 4, 14, 6, 0)
        friday_next_week = datetime(2023, 4, 21, 6, 0)
        for delivery_day in range(10, 17):
            delivery_date = datetime(2023, 4, delivery_day, 12)
            res = self.order_line._apply_customer_window(delivery_date, self.partner)
            if delivery_day < 14:
                # if day is before friday, postpone to saturday this week
                self.assertEqual(res, friday_this_week)
            elif delivery_day == 14:
                # If day is friday (in a time window), keep date as it is
                self.assertEqual(res, delivery_date)
            else:
                # Otherwise, postpone to the next week
                self.assertEqual(res, friday_next_week)

    # sale.order.line._get_latest_work_end_from_date_range

    def test_get_latest_work_end_from_date_range_no_calendar(self):
        self._no_calendar()
        # Say earliest_expedition_date has been computed as monday
        # depending on customer delivery availability, the best_expedition_date
        # might vary
        # However, with no calendar, the input date should be returned
        # without any modification
        earliest_expedition_date = datetime(2023, 4, 10, 12, 0)
        for day in range(10, 17):
            lastest_expedition_date = datetime(2023, 4, day, 12, 0)
            best_expedition_date = self.order_line._get_latest_work_end_from_date_range(
                earliest_expedition_date, lastest_expedition_date
            )
            self.assertEqual(lastest_expedition_date, best_expedition_date)

    def test_get_latest_work_end_from_date_range_with_calendar(self):
        # When the lastest_expedition_date is within a calendar's attendance,
        # then the date is returned without any modification
        kwargs = {"calendar": self.calendar}
        inside_attendance_hour = 12
        earliest_expedition_date = datetime(2023, 4, 10, 12, 0)
        friday_end_of_attendance = datetime(2023, 4, 14, 17, 0)
        for day in range(10, 17):
            lastest_expedition_date = datetime(2023, 4, day, inside_attendance_hour)
            res = self.order_line._get_latest_work_end_from_date_range(
                earliest_expedition_date, lastest_expedition_date, **kwargs
            )
            if day < 15:  # if inside working days, we can send goods right now
                self.assertEqual(res, lastest_expedition_date)
            else:
                # Otherwise, we return the latest expedition date, which is
                # at the end of friday's attendance
                self.assertEqual(res, friday_end_of_attendance)
        # When lastest_expedition_date is outside a calendar's attendance,
        # the returned date is the end of the previous attendance
        after_attendance_hour = 18
        for day in range(10, 17):
            lastest_expedition_date = datetime(2023, 4, day, after_attendance_hour)
            res = self.order_line._get_latest_work_end_from_date_range(
                earliest_expedition_date, lastest_expedition_date, **kwargs
            )
            if day < 15:
                # if inside working days but after the end of an attendance, the right
                # expedition date is the end of the previous attendance (today at 17:00)
                expected_expedition_date = datetime(2023, 4, day, 17, 0)
                self.assertEqual(res, expected_expedition_date)
            else:
                # Otherwise, we return the latest expedition date, which is
                # at the end of friday's attendance
                self.assertEqual(res, friday_end_of_attendance)
        # Just check that if we're past midnight, then the best_expedition_date
        # is moved the day before
        before_attendance_hour = 8
        # Changing values here, because best_expedition_date for 2023-04-10 8:00
        # is 2023-04-07 17:00:00
        for day in range(11, 18):
            lastest_expedition_date = datetime(2023, 4, day, before_attendance_hour)
            res = self.order_line._get_latest_work_end_from_date_range(
                earliest_expedition_date, lastest_expedition_date, **kwargs
            )
            if day < 15:
                # if inside working days but before the start of an attendance
                # (after midnight), the right expedition date is the end of the
                # previous attendance (yesterday at 17:00)
                yesterday = day - 1
                expected_expedition_date = datetime(2023, 4, yesterday, 17, 0)
                self.assertEqual(res, expected_expedition_date)
            else:
                # Otherwise, we return the latest expedition date, which is
                # at the end of friday's attendance
                self.assertEqual(res, friday_end_of_attendance)
        # Now, let's both earliest_expedition_date and lastest_expedition_date
        # are outside an attendance, it means we're already late
        # earliest_expedition_date is the right one
        earliest_expedition_date = datetime(2023, 4, 14, 18, 0)
        lastest_expedition_date = datetime(2023, 4, 17, 6, 0)
        res = self.order_line._get_latest_work_end_from_date_range(
            earliest_expedition_date, lastest_expedition_date, **kwargs
        )
        self.assertEqual(res, earliest_expedition_date)

    # picking._get_delays

    def _add_product_in_order(self, order, product_qties):
        sale_form = Form(order)
        with mute_logger("odoo.tests.common.onchange"):
            for product, qty in product_qties:
                with sale_form.order_line.new() as line:
                    line.product_id = product
                    line.product_uom_qty = qty
        sale_form.save()

    def test_picking_get_delays(self):
        order = self.order
        product = self.env["product.product"].create(
            {"name": "product with delay", "sale_delay": 5, "type": "product"}
        )
        self._add_product_in_order(order, [(product, 10)])
        order.action_confirm()
        picking = order.picking_ids
        # with move_type = direct, get_delays should return the smallest sale_delay
        picking.move_type = "direct"
        sale_delay, __, __ = picking._get_delays()
        self.assertEqual(sale_delay, 1.0)
        # With move_type = one, the biggest one is returned
        picking.move_type = "one"
        sale_delay, __, __ = picking._get_delays()
        self.assertEqual(sale_delay, 5.0)

    def assertDateNotInThePast(self, date_to_check):
        # Be careful, if now frozen, now will change over time
        # and tests might break
        self.assertGreaterEqual(date_to_check, datetime.now())

    @freeze_time("2023-09-05 12:00:00")
    def test_expected_delivery_date_no_commitment_date(self):
        # Ensure that expected_delivery_date is always in the future when
        # no commitment_date is set
        order = self.order
        order.action_confirm()
        picking = order.picking_ids
        delta_1d = timedelta(days=1)
        dates = [
            str(picking.scheduled_date), # 2023-09-06 10:00:00
            str(picking.scheduled_date - delta_1d),# 2023-09-05 10:00:00
            str(picking.scheduled_date + delta_1d),# 2023-09-08 10:00:00
            str(picking.date_deadline), # 2023-09-07 00:00:00
            str(picking.date_deadline - delta_1d), # 2023-09-06 00:00:00
            str(picking.date_deadline + delta_1d), # 2023-09-08 00:00:00
        ]
        for date_ in dates:
            picking.invalidate_cache(["expected_delivery_date"])
            with freeze_time(date_):
                self.assertDateNotInThePast(picking.expected_delivery_date)

    @freeze_time("2023-09-05 12:00:00")
    def test_expected_delivery_date_with_commitment_date(self):
        # Ensure that expected_delivery_date is always in the future when
        # commitment_date is set
        order = self.order
        order.commitment_date = datetime.now()
        order.action_confirm()
        picking = order.picking_ids
        delta_1d = timedelta(days=1)
        dates = [
            str(picking.scheduled_date), # 2023-09-04 10:00:00
            str(picking.scheduled_date - delta_1d), # 2023-09-03 10:00:00
            str(picking.scheduled_date + delta_1d), # 2023-09-05 10:00:00
            str(picking.date_deadline), # 2023-09-05 12:00:00
            str(picking.date_deadline - delta_1d), # 2023-09-04 12:00:00
            str(picking.date_deadline + delta_1d), # 2023-09-06 12:00:00
        ]
        for date_ in dates:
            picking.invalidate_cache(["expected_delivery_date"])
            with freeze_time(date_):
                self.assertDateNotInThePast(picking.expected_delivery_date)

    def test_get_next_open_customer_window_no_partner_no_calendar(self):
        # If no partner nor calendar, date is not postponed
        from_date = datetime(2023, 12, 1 ,0 ,0, 0)
        calendar = self.env["resource.calendar"]
        partner = self.env["res.partner"]
        order_line = self.env["sale.order.line"]
        res = order_line._get_next_open_customer_window(partner, calendar, from_date=from_date)
        self.assertEqual(from_date, res)

    def test_get_delivery_date_from_expedition_date(self):
        order_line_model = self.env["sale.order.line"]
        customer = self.customer_warehouse_cutoff
        calendar = self.calendar
        order_line_model = self.env["sale.order.line"]
        delays = (1, 1, 0) # customer_lead, security_lead, worload
        # Customer is set to receive goods on wednesdays between 12 and 17
        weekday_numbers = (2,)  # Wednesday
        time_window_ranges = [(12.00, 17.00), ]
        self._set_partner_time_window(
            self.customer_warehouse_cutoff, weekday_numbers, time_window_ranges
        )
        # For a customer with delivery preferences set to wednesdays,
        # any date returned by _delivery_date_from_expedition_date should be a
        # wednesday
        delivery_date = order_line_model._delivery_date_from_expedition_date(
            datetime(2024, 1, 8, 0), # 8th of january
            customer, calendar, delays
        )
        self.assertEqual(str(delivery_date.date()), "2024-01-10")
        # If a wednesday is used as expedition date, the next wednesday is returned
        delivery_date = order_line_model._delivery_date_from_expedition_date(
            datetime(2024, 1, 10, 0), # 8th of january
            customer, calendar, delays
        )
        self.assertEqual(str(delivery_date.date()), "2024-01-17")
        # If sale_delivery_date__ignore_customer_window is set in context,
        # the next day is returned, instead of the next customer availability
        order_line_model = order_line_model.with_context(
            sale_delivery_date__ignore_customer_window=True
        )
        delivery_date = order_line_model._delivery_date_from_expedition_date(
            datetime(2024, 1, 8, 0), # 8th of january
            customer, calendar, delays
        )
        self.assertEqual(str(delivery_date.date()), "2024-01-09")
        # If a wednesday is used as expedition date, the next day is returned
        delivery_date = order_line_model._delivery_date_from_expedition_date(
            datetime(2024, 1, 10, 0), # 8th of january
            customer, calendar, delays
        )
        self.assertEqual(str(delivery_date.date()), "2024-01-11")

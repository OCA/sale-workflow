# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time

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
        self._set_partner_time_window_to_friday(self.customer_warehouse_cutoff)
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), NEXT_THURSDAY)
        self.assertEqual(str(order.expected_date.date()), NEXT_FRIDAY)

    @freeze_time(FRIDAY_BEFORE_CUTOFF)
    def test_order_on_friday_before_cutoff_to_deliver_on_friday(self):
        """Order confirmed before cut-off time on Friday to deliver on friday."""
        self._set_partner_time_window_to_friday(self.customer_warehouse_cutoff)
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), NEXT_THURSDAY)
        self.assertEqual(str(order.expected_date.date()), NEXT_FRIDAY)

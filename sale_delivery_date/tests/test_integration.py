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
        order = self._create_order_warehouse_cutoff()
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), FRIDAY)
        self.assertEqual(str(order.expected_date.date()), NEXT_MONDAY)

    @freeze_time(THURSDAY_BEFORE_CUTOFF)
    def test_order_on_thursday_before_cutoff_to_deliver_on_workdays(self):
        """Order confirmed before cut-off time on Thursday to deliver on workdays."""
        order = self._create_order_warehouse_cutoff()
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), THURSDAY)
        self.assertEqual(str(order.expected_date.date()), FRIDAY)

    @freeze_time(FRIDAY_AFTER_CUTOFF)
    def test_order_on_friday_after_cutoff_to_deliver_on_workdays(self):
        """Order confirmed after cut-off time on Friday to deliver on workdays."""
        # Parameters:
        #   - customer_lead = 1
        #   - security_lead = 1
        #   - date_order = "2021-08-20 08:30 UTC" (Friday)
        #   - WH's cutoff time at 10:00 (with TZ)
        #   - WH calendar from 9h to 17h (with TZ)
        #   - no partner's delivery time window
        # Expected result:
        #   - date_planned = "2021-08-23"
        order = self._create_order_warehouse_cutoff()
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(order.expected_date.date()), NEXT_TUESDAY)
        self.assertEqual(str(picking.scheduled_date.date()), NEXT_MONDAY)

    @freeze_time(FRIDAY_BEFORE_CUTOFF)
    def test_order_on_friday_before_cutoff_to_deliver_on_workdays(self):
        """Order confirmed before cut-off time on Friday to deliver on workdays."""
        order = self._create_order_warehouse_cutoff()
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), FRIDAY)
        self.assertEqual(str(order.expected_date.date()), NEXT_MONDAY)

    @freeze_time(FRIDAY_AFTER_CUTOFF)
    def test_order_on_friday_after_cutoff_to_deliver_on_friday(self):
        """Order confirmed after cut-off time on Friday to deliver on friday."""
        self._set_partner_time_window_to_friday(self.customer_warehouse_cutoff)
        self.customer_warehouse_cutoff.delivery_time_window_ids[0].time_window_start = 9
        order = self._create_order_warehouse_cutoff()
        order.action_confirm()
        picking = order.picking_ids
        # Delivery date: Friday 06:00 UTC, so 08:00 with customer's TZ
        self.assertEqual(str(order.expected_date), f"{NEXT_FRIDAY} 07:00:00")
        self.assertEqual(str(picking.date_deadline), f"{NEXT_FRIDAY} 07:00:00")
        # Scheduled date: Thursday 08:00 (in UTC):
        #   - the warehouse cutoff is set to 10:00 GMT+2 (08:00 UTC)
        self.assertEqual(str(picking.scheduled_date), f"{NEXT_THURSDAY} 08:00:00")

    @freeze_time(FRIDAY_BEFORE_CUTOFF)
    def test_order_on_friday_before_cutoff_to_deliver_on_friday(self):
        """Order confirmed before cut-off time on Friday to deliver on friday."""
        self._set_partner_time_window_to_friday(self.customer_warehouse_cutoff)
        self.customer_warehouse_cutoff.delivery_time_window_ids[0].time_window_start = 9
        order = self._create_order_warehouse_cutoff()
        order.action_confirm()
        picking = order.picking_ids
        # Delivery date: Friday 06:00 UTC, so 08:00 with customer's TZ
        self.assertEqual(str(order.expected_date), f"{NEXT_FRIDAY} 07:00:00")
        self.assertEqual(str(picking.date_deadline), f"{NEXT_FRIDAY} 07:00:00")
        # Scheduled date: Thursday 08:00 (in UTC):
        #   - the warehouse cutoff is set to 10:00 GMT+2 (08:00 UTC)
        self.assertEqual(str(picking.scheduled_date), f"{NEXT_THURSDAY} 08:00:00")

    @freeze_time(FRIDAY_BEFORE_CUTOFF)
    def test_order_on_friday_before_cutoff_to_deliver_on_friday_commitment_date(self):
        """Order confirmed before cut-off time on Friday to deliver on friday.

        But here the delivery date is enforced by the commitment_date.
        """
        order = self._create_order_warehouse_cutoff()
        order.commitment_date = f"{NEXT_FRIDAY} 08:00:00"
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(picking.date_deadline, order.commitment_date)
        # The expected date is when we could ship the goods at best if no
        # commitment_date was provided (it's only an indicator for the sale user)
        self.assertEqual(str(order.expected_date.date()), NEXT_MONDAY)
        # The scheduled date is one day before at 08:00 UTC (takes into
        # account the security lead time and in respect to the WH calendar)
        self.assertEqual(str(picking.scheduled_date), f"{NEXT_THURSDAY} 08:00:00")

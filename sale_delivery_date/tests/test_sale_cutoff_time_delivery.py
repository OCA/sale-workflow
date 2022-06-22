# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time

from odoo import fields

from .common import Common

BEFORE_WH_CUTOFF = "09:30:00"
AFTER_WH_CUTOFF = "10:30:00"
BEFORE_PARTNER_CUTOFF = "08:30:00"
AFTER_PARTNER_CUTOFF = "09:30:00"
BEFORE_CUTOFF_TZ = "00:30:00"
AFTER_CUTOFF_TZ = "23:30:00"
MONDAY = "2021-10-04"
TUESDAY = "2021-10-05"
WEDNESDAY = "2021-10-06"
THURSDAY = "2021-10-07"
# NOTE
MONDAY_BEFORE_WH_CUTOFF = f"{MONDAY} {BEFORE_WH_CUTOFF}"
MONDAY_AFTER_WH_CUTOFF = f"{MONDAY} {AFTER_WH_CUTOFF}"
MONDAY_BEFORE_PARTNER_CUTOFF = f"{MONDAY} {BEFORE_PARTNER_CUTOFF}"
MONDAY_AFTER_PARTNER_CUTOFF = f"{MONDAY} {AFTER_PARTNER_CUTOFF}"
# NOTE: the following dates are UTC, with 'Europe/Paris' we are GMT+2
MONDAY_BEFORE_CUTOFF_TZ = f"{MONDAY} {BEFORE_CUTOFF_TZ}"
MONDAY_AFTER_CUTOFF_TZ = f"{MONDAY} {AFTER_CUTOFF_TZ}"


class TestSaleCutoffTimeDelivery(Common):
    @classmethod
    def setUpClassWarehouse(cls):
        super().setUpClassWarehouse()
        cls.apply_cutoff = False
        cls.warehouse.calendar_id = False

    @classmethod
    def setUpClassProduct(cls):
        super().setUpClassProduct()
        cls.product.sale_delay = 1.0

    @classmethod
    def setUpClassCompany(cls):
        super().setUpClassCompany()
        cls.company.security_lead = 1.0

    @classmethod
    def _disable_tz(cls):
        cls.warehouse.tz = False
        cls.customers.tz = False

    @freeze_time(MONDAY_BEFORE_PARTNER_CUTOFF)
    def test_before_partner_cutoff(self):
        self._disable_tz()
        order = self.order_partner_cutoff
        self.assertEqual(str(order.expected_date.date()), TUESDAY)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), MONDAY)

    @freeze_time(MONDAY_BEFORE_WH_CUTOFF)
    def test_before_warehouse_cutoff(self):
        self._disable_tz()
        order = self.order_warehouse_cutoff
        self.assertEqual(str(order.expected_date.date()), TUESDAY)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), MONDAY)

    @freeze_time(MONDAY_AFTER_PARTNER_CUTOFF)
    def test_after_partner_cutoff(self):
        """If order is confirmed after partner cutoff,
        delivery is postponed by 1 day.
        """
        self._disable_tz()
        order = self.order_partner_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(order.expected_date.date()), WEDNESDAY)
        self.assertEqual(str(picking.scheduled_date.date()), TUESDAY)

    @freeze_time(MONDAY_AFTER_WH_CUTOFF)
    def test_after_warehouse_cutoff(self):
        """If order is confirmed after partner cutoff,
        delivery is postponed by 1 day
        """
        self._disable_tz()
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(order.expected_date.date()), WEDNESDAY)
        self.assertEqual(str(picking.scheduled_date.date()), TUESDAY)

    @freeze_time(MONDAY_BEFORE_CUTOFF_TZ)
    def test_before_partner_cutoff_tz(self):
        order = self.order_partner_cutoff
        self.assertEqual(str(order.expected_date.date()), TUESDAY)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), MONDAY)

    @freeze_time(MONDAY_BEFORE_CUTOFF_TZ)
    def test_before_warehouse_cutoff_tz(self):
        order = self.order_warehouse_cutoff
        self.assertEqual(str(order.expected_date.date()), TUESDAY)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), MONDAY)

    @freeze_time(MONDAY_AFTER_CUTOFF_TZ)
    def test_after_partner_cutoff_tz(self):
        """If order is confirmed after partner cutoff,
        delivery is postponed by 1 day.
        """
        order = self.order_partner_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(order.expected_date.date()), WEDNESDAY)
        self.assertEqual(str(picking.scheduled_date.date()), TUESDAY)

    @freeze_time(MONDAY_AFTER_CUTOFF_TZ)
    def test_after_warehouse_cutoff_tz(self):
        """If order is confirmed after partner cutoff,
        delivery is postponed by 1 day
        """
        order = self.order_warehouse_cutoff
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(order.expected_date.date()), WEDNESDAY)
        self.assertEqual(str(picking.scheduled_date.date()), TUESDAY)

    @freeze_time(MONDAY_BEFORE_CUTOFF_TZ)
    def test_commitment_date_partner_cutoff(self):
        order = self.order_partner_cutoff
        order.commitment_date = fields.Datetime.to_datetime(f"{THURSDAY} 16:00:00")
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date), f"{WEDNESDAY} 07:00:00")

# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time
import mock

from odoo import fields
from odoo.tests.common import SavepointCase

MONDAY = fields.Datetime.from_string("2024-03-18")
TUESDAY = fields.Datetime.from_string("2024-03-19")
WEDNESDAY = fields.Datetime.from_string("2024-03-20")


class TestSaleOrderLineCache(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    @freeze_time(MONDAY)
    def test_cache_invalidation(self):
        calendar = self.env.ref("resource.resource_calendar_std")
        sol_model = self.env["sale.order.line"]
        mock_args = (type(calendar), "plan_days")
        mock_kwargs = {"side_effect": calendar.plan_days}
        # First call computes the date
        with mock.patch.object(*mock_args, **mock_kwargs) as mocked:
            date_ = sol_model._add_delay(MONDAY, delay=1, calendar=calendar)
            self.assertEqual(date_.date(), TUESDAY)
            mocked.assert_called()
        # Second call get it from the cache
        with mock.patch.object(*mock_args, **mock_kwargs) as mocked:
            date_ = sol_model._add_delay(MONDAY, delay=1, calendar=calendar)
            self.assertEqual(date_.date(), TUESDAY)
            mocked.assert_not_called()
        # Update the calendar data to invalidate the cache so the date is
        # computed from the calendar again
        with mock.patch.object(*mock_args, **mock_kwargs) as mocked:
            calendar.write({})
            date_ = sol_model._add_delay(MONDAY, delay=1, calendar=calendar)
            self.assertEqual(date_.date(), TUESDAY)
            mocked.assert_called()
        # Same by updating the attendances to invalidate the cache
        with mock.patch.object(*mock_args, **mock_kwargs) as mocked:
            calendar.attendance_ids.write({})
            date_ = sol_model._add_delay(MONDAY, delay=1, calendar=calendar)
            self.assertEqual(date_.date(), TUESDAY)
            mocked.assert_called()
        # Same by updating the leaves to invalidate the cache
        with mock.patch.object(*mock_args, **mock_kwargs) as mocked:
            calendar.leave_ids.write({})
            date_ = sol_model._add_delay(MONDAY, delay=1, calendar=calendar)
            self.assertEqual(date_.date(), TUESDAY)
            mocked.assert_called()
        # Using the cache again
        with mock.patch.object(*mock_args, **mock_kwargs) as mocked:
            date_ = sol_model._add_delay(MONDAY, delay=1, calendar=calendar)
            self.assertEqual(date_.date(), TUESDAY)
            mocked.assert_not_called()
        # Not using the cache with different parameters
        with mock.patch.object(*mock_args, **mock_kwargs) as mocked:
            date_ = sol_model._add_delay(MONDAY, delay=2, calendar=calendar)
            self.assertEqual(date_.date(), WEDNESDAY)
            mocked.assert_called()

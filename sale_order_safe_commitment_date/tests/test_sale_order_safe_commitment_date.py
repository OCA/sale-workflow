# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from freezegun import freeze_time

from odoo.tests import Form, TransactionCase


@freeze_time("2018-01-11")
class TestSaleOrderSafeCommitmentDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Make sure everything is on the same timezone
        cls.env.user.tz = "UTC"
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        calendar = cls.env["resource.calendar"].create(
            {"name": "Sales cut-off", "tz": "UTC"}
        )
        cls.env["resource.calendar.attendance"].create(
            [
                {
                    "name": "Sales cut-off",
                    "calendar_id": calendar.id,
                    "dayofweek": str(day),
                    "day_period": "afternoon",
                    "hour_from": 0,
                    "hour_to": 20,
                }
                for day in range(7)
            ]
        )
        cls.env.company.sales_cutoff_calendar = calendar
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test thingy",
                "sale_delay": 2,
            }
        )
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with sale_form.order_line.new() as line:
            line.product_id = cls.product
        cls.sale_order = sale_form.save()

    def test_unsafe_commitment_date(self):
        """Time is freezed at 2018-01-11. As there aren't lead times, expected date
        will be that date. Any date previous to that one is unsafe"""
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        # Always in the past. Impossible to fulfill
        self.sale_order.commitment_date = "2018-01-10"
        self.assertTrue(self.sale_order.is_commitment_date_unsafe)
        self.sale_order.action_confirm()
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        self.assertEqual(
            self.sale_order.date_for_commitment,
            self.sale_order.expected_day,
            "After confirmation, commitment date should match expected date",
        )

    @freeze_time("2018-01-11 19:59:00")
    def test_safe_commitment_date(self):
        """Time is freezed at 2018-01-11. There aren't lead times and the commitment
        date is set after the expected date"""
        self.assertFalse(self.sale_order.in_sale_cutoff_hour)
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        # Let's put a safe commitment date
        self.sale_order.commitment_date = "2018-01-13"
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        self.sale_order.action_confirm()
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        # Should preserve the commitment date
        self.assertEqual(str(self.sale_order.date_for_commitment), "2018-01-13")

    @freeze_time("2018-01-11 20:01:00")
    def test_cutoff_hour(self):
        """The same test as before, but we're in sales cut-off"""
        self.assertTrue(self.sale_order.in_sale_cutoff_hour)
        # The date isn't safe anymore
        self.sale_order.commitment_date = "2018-01-13"
        self.assertTrue(self.sale_order.is_commitment_date_unsafe)

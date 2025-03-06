# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderRequestedDelivery(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env.ref("sale.sale_order_1")
        cls.sale_order.write(
            {
                "requested_delivery_period_start": "2024-01-21 10:00:00",
                "requested_delivery_period_end": "2024-02-13 18:00:00",
            }
        )
        lang = cls.env["res.lang"]._lang_get(cls.env.user.lang or "en_US")
        cls.start_date = cls.sale_order.requested_delivery_period_start.strftime(
            lang.date_format
        )
        cls.end_date = cls.sale_order.requested_delivery_period_end.strftime(
            lang.date_format
        )

    def test_requested_delivery_period_display_both_dates(self):
        self.assertEqual(
            self.sale_order.requested_delivery_period_display,
            f"{self.start_date} - {self.end_date}",
        )

    def test_requested_delivery_period_display_start_date_only(self):
        self.sale_order.requested_delivery_period_end = False
        self.assertEqual(
            self.sale_order.requested_delivery_period_display, f"From {self.start_date}"
        )

    def test_requested_delivery_period_display_end_date_only(self):
        self.sale_order.requested_delivery_period_start = False
        self.assertEqual(
            self.sale_order.requested_delivery_period_display, f"Until {self.end_date}"
        )

    def test_requested_delivery_period_display_no_dates(self):
        self.sale_order.requested_delivery_period_start = False
        self.sale_order.requested_delivery_period_end = False
        self.assertEqual(self.sale_order.requested_delivery_period_display, "N/A")

    def test_requested_delivery_period_start_after_end(self):
        with self.assertRaisesRegex(
            ValidationError,
            "The start of the requested delivery period cannot be after the end.",
        ):
            self.sale_order.requested_delivery_period_end = "2024-01-20 10:00:00"

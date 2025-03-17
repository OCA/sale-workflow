# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLineRequestedDelivery(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_line = cls.env.ref("sale.sale_order_line_1")
        cls.sale_order_line.write(
            {
                "requested_delivery_period_start": "2024-01-21 10:00:00",
                "requested_delivery_period_end": "2024-02-13 18:00:00",
            }
        )

    def test_requested_delivery_period_start_after_end(self):
        with self.assertRaisesRegex(
            ValidationError,
            "The start of the requested delivery period cannot be after the end.",
        ):
            self.sale_order_line.requested_delivery_period_end = "2024-01-20 10:00:00"

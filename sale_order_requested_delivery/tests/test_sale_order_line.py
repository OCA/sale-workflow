# Copyright 2024 CamptoCamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLineRequestedDelivery(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.sale_order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
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

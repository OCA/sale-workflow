# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.sale_order_line_final_price.tests import (
    test_sale_order_line_final_price,
)


@tagged("post_install", "-at_install")
class TestSaleOrderLineFinalPrice(
    test_sale_order_line_final_price.TestSaleOrderLineFinalPrice
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_delivery = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "service",
                "list_price": 0,
                "taxes_id": False,
            }
        )

    def test_price_final_delivery(self):
        """The line is created with the agreed price as its unit price, and the
        amounts take it into account."""
        self.order.order_line = [
            Command.create(
                {"product_id": self.product_delivery.id, "is_delivery": True}
            )
        ]
        line = self.order.order_line[-1]
        line.price_final = 50
        self.assertEqual(line.price_unit, 50)
        self.assertEqual(line.discount, 0)
        line.price_final = 100
        self.assertEqual(line.price_unit, 100)

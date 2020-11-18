# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestDeliveryLinePrice(common.SavepointCase):
    """Test class for delivery line price extension."""

    @classmethod
    def setUpClass(cls):
        """Set up data for tests."""
        super().setUpClass()
        cls.ChooseDeliveryCarrier = cls.env["choose.delivery.carrier"]
        cls.sale_3 = cls.env.ref("sale.sale_order_3")
        cls.delivery_normal = cls.env.ref("delivery.normal_delivery_carrier")
        # Make it free if above threshold.
        cls.delivery_normal.write({"free_over": True, "amount": 100})
        cls.choose_delivery_carrier = cls.ChooseDeliveryCarrier.create(
            {"order_id": cls.sale_3.id, "carrier_id": cls.delivery_normal.id}
        )
        cls.promotion_10_percent = cls.env.ref("sale_coupon.10_percent_auto_applied")

    def _get_delivery_line_price(self, order):
        return order.order_line.filtered("is_delivery")[0]["price_unit"]

    def test_01_test_delivery_line_price(self):
        """Recompute SO to see if delivery price is set correctly.

        Case 1: add delivery line (free shipping threshold met)
        Case 2: recompute promotions (free shipping threshold met).
        """
        # Case 1.
        self.choose_delivery_carrier.button_confirm()
        self.assertEqual(self._get_delivery_line_price(self.sale_3), 0)
        # Case 2.
        self.sale_3.recompute_coupon_lines()
        self.assertEqual(self._get_delivery_line_price(self.sale_3), 0)

    def test_02_test_delivery_line_price(self):
        """Recompute SO to see if delivery price is set correctly.

        Case 1: add delivery line (free shipping threshold met)
        Case 2: recompute promotions (free shipping threshold not met).
        """
        # Case 1.
        self.choose_delivery_carrier.button_confirm()
        self.assertEqual(self._get_delivery_line_price(self.sale_3), 0)
        # Case 2.
        # To apply automatically.
        self.promotion_10_percent.promo_code_usage = "no_code_needed"
        # To not reach threshold after promotion is applied.
        self.delivery_normal.amount = 350
        self.sale_3.recompute_coupon_lines()
        self.assertEqual(self._get_delivery_line_price(self.sale_3), 10)

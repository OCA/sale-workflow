# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestDiscountApplyOnWithDelivery(SavepointCase):
    """Test class for discount_apply_on customization tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Records.
        # Programs.
        cls.program_promotion_code = cls.env.ref("sale_coupon.10_percent_auto_applied")
        cls.program_promotion_code.promo_code_usage = "no_code_needed"
        cls.program_promotion_code.discount_apply_on = "most_expensive_product"
        # Sales.
        # amount_total = 9705
        cls.sale_1 = cls.env.ref("sale.sale_order_1")
        cls.sale_1_line_most_expensive = cls.env.ref("sale.sale_order_line_1")
        # Deliveries
        cls.carrier_normal = cls.env.ref("delivery.normal_delivery_carrier")

    def _apply_delivery_on_sale(self, sale, delivery):
        delivery_wizard = (
            self.env["choose.delivery.carrier"]
            .with_context(default_order_id=sale.id, default_carrier_id=delivery.id)
            .create({})
        )
        delivery_wizard.update_price()
        delivery_wizard.button_confirm()

    def test_01_discount_apply_on_with_delivery(self):
        """Apply 10% on most expensive product (line)."""

        # Compute expected amounts
        big_delivery_amount = 100000
        most_expensive_price_disc = self.sale_1_line_most_expensive.price_unit * 0.1
        expected_amount_total = self.sale_1.amount_total - most_expensive_price_disc
        expected_amount_total_with_delivery = (
            expected_amount_total + self.carrier_normal.fixed_price
        )
        expected_amount_total_with_big_delivery = (
            expected_amount_total + big_delivery_amount
        )

        # Test without delivery
        self.sale_1.recompute_coupon_lines()
        self.assertEqual(self.sale_1.amount_total, expected_amount_total)

        # Test with normal delivery (lower than most expensive product)
        self.assertTrue(
            self.sale_1_line_most_expensive.price_unit > self.carrier_normal.fixed_price
        )
        self._apply_delivery_on_sale(self.sale_1, self.carrier_normal)
        self.sale_1.recompute_coupon_lines()
        self.assertEqual(self.sale_1.amount_total, expected_amount_total_with_delivery)

        # Test with big delivery (higher than most expensive product)
        # Reward is still computed on the most expensive product ignoring deliveries
        self.carrier_normal.fixed_price = big_delivery_amount
        self.assertTrue(
            self.sale_1_line_most_expensive.price_unit < self.carrier_normal.fixed_price
        )
        self._apply_delivery_on_sale(self.sale_1, self.carrier_normal)
        self.sale_1.recompute_coupon_lines()
        self.assertEqual(
            self.sale_1.amount_total, expected_amount_total_with_big_delivery
        )

# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestDiscountApplyOn(SavepointCase):
    """Test class for discount_apply_on customization tests."""

    @classmethod
    def setUpClass(cls):
        """Set up common data for multi use coupon tests."""
        super().setUpClass()
        # Models.
        cls.SaleCoupon = cls.env["sale.coupon"]
        cls.SaleCouponProgram = cls.env["sale.coupon.program"]
        cls.SaleCouponGenerate = cls.env["sale.coupon.generate"]
        cls.SaleCouponApplyCode = cls.env["sale.coupon.apply.code"]
        # Records.
        # Coupon Programs.
        # cls.program_coupon_percentage = cls.env.ref("sale_coupon.10_percent_coupon")
        cls.program_promotion_code = cls.env.ref("sale_coupon.10_percent_auto_applied")
        # Sales.
        # amount_total = 9705
        cls.sale_1 = cls.env.ref("sale.sale_order_1")
        cls.sale_1_line_most_expensive = cls.env.ref("sale.sale_order_line_1")
        cls.sale_1_line_cheapest = cls.env.ref("sale.sale_order_line_3")
        # amount_total = 2947.5
        cls.sale_2 = cls.env.ref("sale.sale_order_2")
        cls.wizard_apply_code = cls.SaleCouponApplyCode.with_context(
            active_id=cls.sale_1.id
        ).create({"coupon_code": cls.program_promotion_code.promo_code})

    def test_01_discount_apply_on(self):
        """Apply 10% on whole order."""
        expected_amount_total = self.sale_1.amount_total * 0.9
        self.wizard_apply_code.process_coupon()
        self.assertEqual(self.sale_1.amount_total, expected_amount_total)

    def test_02_discount_apply_on(self):
        """Apply 10% on cheapest product (line)."""
        cheapest_price_disc = self.sale_1_line_cheapest.price_unit * 0.1
        expected_amount_total = self.sale_1.amount_total - cheapest_price_disc
        self.program_promotion_code.discount_apply_on = "cheapest_product"
        self.wizard_apply_code.process_coupon()
        self.assertEqual(self.sale_1.amount_total, expected_amount_total)

    def test_03_discount_apply_on(self):
        """Apply 10% on most expensive product (line)."""
        most_expensive_price_disc = self.sale_1_line_most_expensive.price_unit * 0.1
        expected_amount_total = self.sale_1.amount_total - most_expensive_price_disc
        self.program_promotion_code.discount_apply_on = "most_expensive_product"
        self.wizard_apply_code.process_coupon()
        self.assertEqual(self.sale_1.amount_total, expected_amount_total)

    def test_04_reward_display_name(self):
        """Get reward display name that is applied on most exp prod."""
        self.program_promotion_code.discount_apply_on = "most_expensive_product"
        self.assertEqual(
            self.program_promotion_code.reward_id.display_name,
            "10.0% discount on most expensive product",
        )

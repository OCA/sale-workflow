import re

from odoo.exceptions import UserError
from odoo.tests import common


class TestSaleCouponCustomCode(common.SavepointCase):
    """Test class for custom coupon code generation."""

    @classmethod
    def setUpClass(cls):
        """Set up data for custom coupon code generation."""
        super().setUpClass()
        cls.SaleCouponGenerate = cls.env["sale.coupon.generate"]
        cls.SaleCouponProgram = cls.env["sale.coupon.program"]
        cls.SaleCoupon = cls.env["sale.coupon"]
        cls.coupon_program_1 = cls.SaleCouponProgram.create(
            {
                "name": "Test Coupon Program",
                "program_type": "coupon_program",
                "promo_code_usage": "code_needed",
                "reward_type": "discount",
            }
        )
        cls.coupon_generate_1 = cls.SaleCouponGenerate.with_context(
            active_id=cls.coupon_program_1.id
        ).create({})

    def _generate_coupon_code(self, wizard):
        wizard.generate_coupon()
        program = self.SaleCouponProgram.browse(wizard._context.get("active_id"))
        return program.coupon_ids[-1]

    def test_01_code_generation(self):
        """Generate custom code with prefix ABC and 5 random symbols."""
        self.coupon_generate_1.write(
            {"custom_code_generation": True, "custom_code_prefix": "ABC"}
        )
        coupon = self._generate_coupon_code(self.coupon_generate_1)
        self.assertTrue(coupon.code.startswith("ABC"))
        self.assertEqual(len(coupon.code), 8)

    def test_02_code_generation(self):
        """Generate custom code with prefix '' and 6 random symbols."""
        self.coupon_generate_1.write(
            {"custom_code_generation": True, "custom_code_nbr": 6}
        )
        coupon = self._generate_coupon_code(self.coupon_generate_1)
        self.assertEqual(len(coupon.code), 6)

    def test_03_code_generation(self):
        """Try to generate custom code with custom_code_nbr == 0."""
        self.coupon_generate_1.write(
            {"custom_code_generation": True, "custom_code_nbr": 0}
        )
        with self.assertRaises(UserError):
            self._generate_coupon_code(self.coupon_generate_1)

    def test_04_code_generation(self):
        """Generate standard coupon code."""
        coupon = self._generate_coupon_code(self.coupon_generate_1)
        # Standard coupon code must have all symbols as digits.
        self.assertTrue(re.match(r"^\d+$", coupon.code))

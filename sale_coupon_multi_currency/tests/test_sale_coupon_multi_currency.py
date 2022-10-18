# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from .common import TestSaleCouponMultiCurrencyCommon


class TestSaleCouponMultiCurrency(TestSaleCouponMultiCurrencyCommon):
    """Test custom currency on program."""

    def test_01_program_multi_currency(self):
        """Set custom currency.

        Case 1: set custom currency other than company currency.
        Case 2: unset custom currency to use company currency.
        """
        # Case 1.
        self.program_coupon_percentage.currency_id = self.currency_other.id
        self.assertEqual(
            self.program_coupon_percentage.currency_id, self.currency_other
        )
        self.assertEqual(
            self.program_coupon_percentage.currency_custom_id, self.currency_other
        )
        self.assertEqual(self.company_main.currency_id, self.currency_company)
        # Case 2.
        self.program_coupon_percentage.currency_custom_id = False
        self.assertEqual(
            self.program_coupon_percentage.currency_id, self.currency_company
        )
        self.assertFalse(self.program_coupon_percentage.currency_custom_id)
        self.assertEqual(self.company_main.currency_id, self.currency_company)

    def test_02_program_multi_currency(self):
        """Set custom currency on create."""
        program = self.env["sale.coupon.program"].create(
            {"name": "Test", "currency_id": self.currency_other.id}
        )
        self.assertEqual(program.currency_id, self.currency_other)
        self.assertEqual(program.currency_custom_id, self.currency_other)

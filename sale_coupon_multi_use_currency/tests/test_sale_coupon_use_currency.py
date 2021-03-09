# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError

from odoo.addons.sale_coupon_multi_currency.tests.common import (
    TestSaleCouponMultiCurrencyCommon,
)
from odoo.addons.sale_coupon_multi_use.tests.common import TestSaleCouponMultiUseCommon


class TestSaleCouponUseCurrency(
    TestSaleCouponMultiCurrencyCommon, TestSaleCouponMultiUseCommon
):
    """Test class for coupon multi use with currency."""

    def test_01_check_currency_custom_id(self):
        """Check program currency when multi use coupon is generated.

        Case: multi_use=True
        """
        with self.assertRaises(ValidationError) as error:
            self.program_multi_use.currency_custom_id = self.currency_other
        self.assertTrue(
            "Currency can't be changed when there are Multi"
            " Use coupons already." in error.exception.name
        )
        # Without coupons we can change currency
        self.program_multi_use.coupon_ids.unlink()
        self.program_multi_use.currency_custom_id = self.currency_other

    def test_02_check_currency_custom_id(self):
        """Check program currency when multi use coupon is generated.

        Case: multi_use=False
        """
        # Remove coupons because
        # we can't change coupon_multi_use flag when existing coupons
        self.program_multi_use.coupon_ids.unlink()
        self.program_multi_use.coupon_multi_use = False
        self.coupon_generate_wiz.generate_coupon()
        self.program_multi_use.currency_custom_id = self.currency_other

    def test_03_check_currency_custom_id(self):
        """Check program currency when multi use coupon is not generated.

        Case 1: multi_use=True
        Case 2: multi_use=False
        """

        def pass_currency(program):
            fail_msg = (
                "There are no multi use coupons generated, so must be able"
                " to change currency_custom_id."
            )
            try:
                program.currency_custom_id = self.currency_other.id
            except ValidationError:
                self.fail(fail_msg)

        # Copy program, so it would not have coupons.
        program = self.program_multi_use.copy()
        # Case 1.
        pass_currency(program)
        # Case 2.
        program.coupon_multi_use = False
        pass_currency(program)

# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import Form

from .common import (
    CODE_COUPON_PROGRAM,
    NAME_COUPON_PROGRAM,
    TestSaleCouponProductManageCommon,
)


class TestSaleCouponManage(TestSaleCouponProductManageCommon):
    """Test class for program management use cases."""

    def test_01_program_discount_product_rel_vals(self):
        """Check created program with related product.

        Check if related values are propagated to related product.

        Case 1: create promotion initially.
        Case 2: update promotion/related product related values.
        """
        # Case 1.
        program = self.program
        product = program.discount_line_product_id
        self.assertEqual(product.default_code, CODE_COUPON_PROGRAM)
        self.assertEqual(product.categ_id, self.product_category_program)
        # Must match program name exactly.
        self.assertEqual(product.name, NAME_COUPON_PROGRAM)
        # Case 2.
        name_2 = "Product Name"
        # Clear context, so it would be treated as separate update.
        product = product.with_context(forced_product_vals={})
        product.name = name_2
        self.assertEqual(program.name, NAME_COUPON_PROGRAM)
        self.assertEqual(product.name, name_2)
        name_3 = "Program Name"
        program.name = name_3
        self.assertEqual(program.name, name_3)
        self.assertEqual(product.name, name_3)
        # Make sure old dependencies dont update name the old way.
        program.discount_fixed_amount = 300
        self.assertEqual(program.name, name_3)
        self.assertEqual(product.name, name_3)
        code_2 = "MYCODE321"
        program.force_product_default_code = code_2
        self.assertEqual(product.default_code, code_2)
        program.discount_line_product_id.default_code = CODE_COUPON_PROGRAM
        self.assertEqual(product.default_code, CODE_COUPON_PROGRAM)
        # Sanity check.
        self.assertFalse(product.sale_ok)

    def test_02_program_discount_product_rel_vals(self):
        """Check if option values are passed to product.

        Case: on program create - passing sale_ok, lst_price.
        """
        self.product_category_program.write(
            {
                "program_product_sale_ok": True,
                "program_product_discount_fixed_amount": True,
            }
        )
        program = self.SaleCouponProgram.create(
            {
                "name": "Coupon Program 2",
                "program_type": "coupon_program",
                "reward_type": "discount",
                "discount_type": "fixed_amount",
                "discount_fixed_amount": 1000,
                "force_product_default_code": CODE_COUPON_PROGRAM,
                "force_product_categ_id": self.product_category_program.id,
            }
        )
        product = program.discount_line_product_id
        self.assertTrue(product.sale_ok)
        self.assertEqual(product.lst_price, 1000)

    def test_03_check_program_options(self):
        """Validate if program values match its related options.

        Case 1: values match.
        Case 2: values not match.
        """
        # Case 1.
        self.program.force_product_categ_id = self.product_category_not_program
        product = self.program.discount_line_product_id
        product.sale_ok = True  # to not trigger constraint on product.
        self.product_category_program.write(
            {
                "program_product_sale_ok": True,
                "program_product_discount_fixed_amount": True,
            }
        )
        self.program.force_product_categ_id = self.product_category_program
        # Case 2.
        with self.assertRaises(UserError):
            self.program.discount_type = "percentage"
        with self.assertRaises(UserError):
            self.program.reward_type = "product"

    def test_04_check_product_options(self):
        """Validate if program product values match its related options.

        Case 1: values match.
        Case 2: values not match.
        """
        # Case 1.
        product = self.program.discount_line_product_id
        product.write(
            {"sale_ok": True, "categ_id": self.product_category_not_program.id}
        )
        self.product_category_program.write(
            {
                "program_product_sale_ok": True,
                "program_product_discount_fixed_amount": True,
            }
        )
        product.categ_id = self.product_category_program.id
        # Case 2.
        with self.assertRaises(UserError):
            product.sale_ok = False

    def test_05_default_promotion_next_order_category(self):
        """Check if default category is set on next order type promo.

        Case 1: onchange with promo_applicability = on_current_order
        Case 2: onchange with promo_applicability = on_next_order
        Case 3: check if only one default categ can be used.
        """
        # Case 1.
        self.product_category_program_default.default_promotion_next_order_category = (
            True
        )
        with Form(
            self.SaleCouponProgram,
            view="sale_coupon.sale_coupon_program_view_promo_program_form",
        ) as program:
            program.name = "Promotion Program"
            program.program_type = "promotion_program"
            program.promo_applicability = "on_current_order"
            program.reward_type = "discount"
            program.discount_type = "fixed_amount"
            program.discount_fixed_amount = 1000
            program.force_product_default_code = CODE_COUPON_PROGRAM
            self.assertFalse(program.force_product_categ_id)
            # Case 2.
            program.promo_applicability = "on_next_order"
            self.assertEqual(
                program.force_product_categ_id, self.product_category_program_default
            )

    def test_06_onchange_product_categ_with_opts(self):
        """Onchange product category that has program option."""
        product = self.program.discount_line_product_id
        self.assertFalse(product.sale_ok)
        self.product_category_program.program_product_sale_ok = True
        with Form(product) as p:
            p.categ_id = self.product_category_program
            self.assertTrue(p.sale_ok)

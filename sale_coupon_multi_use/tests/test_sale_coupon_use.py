# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Date

from .common import DISCOUNT_AMOUNT, TestSaleCouponMultiUseCommon

_today = Date.today()


class TestSaleCouponMultiUse(TestSaleCouponMultiUseCommon):
    """Test class for coupon multi use cases."""

    def _separate_pricelist_company_currency(self, pricelist, company):
        if pricelist.currency_id == company.currency_id:
            # Make pricelist currency different than company one.
            if pricelist.currency_id == self.eur:
                pricelist.currency_id = self.usd
            else:
                pricelist.currency_id = self.eur
        return pricelist.currency_id, company.currency_id

    def _cmp_record_ids(self, rec1, rec2):
        self.assertEqual(
            sorted(rec1.ids), sorted(rec2.ids), "{} not equal to {}".format(rec1, rec2)
        )

    def _remove_so_discount_lines(self, order):
        order.order_line.filtered("is_reward_line").unlink()

    def test_01_coupon_single_use(self):
        """Apply coupon normally without multi_use functionality."""
        # Sanity check.
        self.assertTrue(self.coupon_multi_use_1.multi_use)
        # Remove coupons because
        # we can't change coupon_multi_use flag when existing coupons
        self.program_multi_use.coupon_ids.unlink()
        self.program_multi_use.coupon_multi_use = False
        # Generate second coupon.
        self.coupon_generate_wiz.generate_coupon()
        coupon_2 = self.program_multi_use.coupon_ids
        self.assertFalse(coupon_2.multi_use)
        self.coupon_apply_wiz.coupon_code = coupon_2.code
        amount_total_expected = self.sale_1.amount_total - DISCOUNT_AMOUNT
        self.coupon_apply_wiz.with_context(active_id=self.sale_1.id).process_coupon()
        # Sanity check.
        self.assertEqual(self.sale_1.amount_total, amount_total_expected)
        self.assertFalse(self.coupon_multi_use_1.consumption_line_ids)
        self.assertFalse(self.sale_1.coupon_multi_use_ids)

    def test_02_coupon_multi_use(self):
        """Apply coupon to consume all amount in one use.

        Case 1: consume all value on single SO.
        Case 2: try to consume again on another SO.
        Case 3: remove discount on SO line.
        """
        # Case 1.
        # SO 1 amount 9705 > 5000.
        amount_total_orig = self.sale_1.amount_total
        amount_total_expected = amount_total_orig - DISCOUNT_AMOUNT
        self.coupon_apply_wiz.with_context(active_id=self.sale_1.id).process_coupon()
        self.assertEqual(self.sale_1.amount_total, amount_total_expected)
        consume_lines = self.coupon_multi_use_1.consumption_line_ids
        self.assertEqual(len(consume_lines), 1)
        self.assertEqual(consume_lines[0].amount, DISCOUNT_AMOUNT)
        self.assertEqual(self.coupon_multi_use_1.discount_fixed_amount_delta, 0)
        self.assertEqual(self.coupon_multi_use_1.state, "used")
        # Check if multi-coupons were applied.
        self.assertEqual(self.sale_1.coupon_multi_use_ids, self.coupon_multi_use_1)
        # Case 2.
        with self.assertRaises(UserError):
            self.coupon_apply_wiz.with_context(
                active_id=self.sale_2.id
            ).process_coupon()
        # Case 3.
        self._remove_so_discount_lines(self.sale_1)
        self.assertEqual(self.sale_1.amount_total, amount_total_orig)
        self.assertFalse(self.coupon_multi_use_1.consumption_line_ids)
        self.assertEqual(
            self.coupon_multi_use_1.discount_fixed_amount_delta, DISCOUNT_AMOUNT
        )
        self.assertEqual(self.coupon_multi_use_1.state, "new")

    def test_03_coupon_multi_use(self):
        """Apply coupon to consume all amount in two uses.

        Case 1: consume part of coupon amount on SO2.
        Case 2: consume remaining amount on SO1.
        Case 3: remove discount from SO1.
        Case 4: remove discount from SO2.
        """
        # Case 1:
        amount_total_orig_1 = self.sale_2.amount_total
        amount_total_expected = 0  # must make SO free.
        self.coupon_apply_wiz.with_context(active_id=self.sale_2.id).process_coupon()
        self.assertEqual(self.sale_2.amount_total, amount_total_expected)
        consumption_line_so_2 = self.coupon_multi_use_1.consumption_line_ids
        self.assertEqual(len(consumption_line_so_2), 1)
        self.assertEqual(consumption_line_so_2[0].amount, amount_total_orig_1)
        remaining_discount = DISCOUNT_AMOUNT - amount_total_orig_1
        # Delta showing left amount that can be consumed.
        self.assertEqual(
            self.coupon_multi_use_1.discount_fixed_amount_delta, remaining_discount
        )
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        # Check if multi-coupons were applied.
        self.assertEqual(self.sale_2.coupon_multi_use_ids, self.coupon_multi_use_1)
        self.assertEqual(self.coupon_multi_use_1.sale_multi_use_ids, self.sale_2)
        # Case 2.
        amount_total_expected = self.sale_1.amount_total - remaining_discount
        self.coupon_apply_wiz.with_context(active_id=self.sale_1.id).process_coupon()
        self.assertEqual(self.sale_1.amount_total, amount_total_expected)
        consume_lines = self.coupon_multi_use_1.consumption_line_ids
        self.assertEqual(len(consume_lines), 2)
        # First consumed amount is total of first whole SO total.
        self.assertEqual(consume_lines[0].amount, amount_total_orig_1)
        # Second consumed amount is all remaining coupon value.
        self.assertEqual(consume_lines[1].amount, remaining_discount)
        self.assertEqual(self.coupon_multi_use_1.discount_fixed_amount_delta, 0)
        self.assertEqual(self.coupon_multi_use_1.state, "used")
        # Check if another SO was related with multi use coupon.
        self.assertEqual(self.sale_2.coupon_multi_use_ids, self.coupon_multi_use_1)
        self.assertEqual(self.sale_1.coupon_multi_use_ids, self.coupon_multi_use_1)
        self._cmp_record_ids(
            self.coupon_multi_use_1.sale_multi_use_ids, self.sale_1 | self.sale_2
        )
        # Case 3.
        self._remove_so_discount_lines(self.sale_1)
        consume_lines = self.coupon_multi_use_1.consumption_line_ids
        # Should have only line that is related with SO2.
        self.assertEqual(
            self.coupon_multi_use_1.consumption_line_ids, consumption_line_so_2
        )
        # Amount on existing line must be unchanged.
        self.assertEqual(consumption_line_so_2.amount, amount_total_orig_1)
        # Should have remaining amount as it had when only SO2 used
        # coupon.
        self.assertEqual(
            self.coupon_multi_use_1.discount_fixed_amount_delta, remaining_discount
        )
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        # Check if coupon was removed following removed SO line.
        self.assertEqual(self.sale_2.coupon_multi_use_ids, self.coupon_multi_use_1)
        self.assertFalse(self.sale_1.coupon_multi_use_ids)
        self.assertEqual(self.coupon_multi_use_1.sale_multi_use_ids, self.sale_2)
        # Case 4.
        self._remove_so_discount_lines(self.sale_2)
        self.assertFalse(self.coupon_multi_use_1.consumption_line_ids)
        self.assertEqual(
            self.coupon_multi_use_1.discount_fixed_amount_delta, DISCOUNT_AMOUNT
        )
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        # Check if both SO are now unrelated with multi-use coupon.
        self.assertFalse(self.sale_1.coupon_multi_use_ids)
        self.assertFalse(self.sale_2.coupon_multi_use_ids)

    def test_04_coupon_multi_use(self):
        """Apply multi use coupon on SO with different currency.

        Case 1: consume part of coupon amount on SO2.
        Case 2: consume remaining amount on SO1.
        """
        (
            currency_pricelist,
            currency_company,
        ) = self._separate_pricelist_company_currency(
            self.pricelist_public, self.company_main
        )
        # Case 1.
        amount_total_orig_1 = self.sale_2.amount_total
        amount_total_expected = 0  # must make SO free.
        self.coupon_apply_wiz.with_context(active_id=self.sale_2.id).process_coupon()
        self.assertEqual(self.sale_2.amount_total, amount_total_expected)
        consumption_line_so_2 = self.coupon_multi_use_1.consumption_line_ids
        self.assertEqual(len(consumption_line_so_2), 1)
        amount_consumption_line_1 = currency_pricelist._convert(
            amount_total_orig_1, currency_company, self.company_main, _today
        )
        self.assertEqual(consumption_line_so_2[0].amount, amount_consumption_line_1)
        # In company currency
        remaining_discount = DISCOUNT_AMOUNT - amount_consumption_line_1
        # Delta showing left amount that can be consumed.
        self.assertAlmostEqual(
            self.coupon_multi_use_1.discount_fixed_amount_delta,
            remaining_discount,
            places=8,
        )
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        # Case 2.
        amount_total_expected = self.sale_1.amount_total - currency_company._convert(
            remaining_discount, currency_pricelist, self.company_main, _today,
        )
        self.coupon_apply_wiz.with_context(active_id=self.sale_1.id).process_coupon()
        self.assertEqual(self.sale_1.amount_total, amount_total_expected)  # USD
        consume_lines = self.coupon_multi_use_1.consumption_line_ids
        self.assertEqual(len(consume_lines), 2)
        # First consumed amount is total of first whole SO total.
        self.assertEqual(consume_lines[0].amount, amount_consumption_line_1)
        # Second consumed amount is all remaining coupon value.
        self.assertAlmostEqual(consume_lines[1].amount, remaining_discount, places=8)
        self.assertEqual(self.coupon_multi_use_1.discount_fixed_amount_delta, 0)
        self.assertEqual(self.coupon_multi_use_1.state, "used")

    def test_05_coupon_multi_use(self):
        """Apply multiple coupons and confirm SO.

        Case 1: apply first coupon (single use).
        Case 2: apply second coupon (multi use) and confirm SO.
        """
        # Prepare second multi use coupon from different program.
        discount_amount_2 = 100
        program_coupon = self.program_multi_use.copy(
            default={
                "discount_fixed_amount": discount_amount_2,
                "coupon_multi_use": False,
            }
        )
        self.SaleCouponGenerate.with_context(active_id=program_coupon.id).create(
            {}
        ).generate_coupon()
        coupon = program_coupon.coupon_ids[0]
        coupon_apply_wiz_2 = self.SaleCouponApplyCode.create(
            {"coupon_code": coupon.code}
        )
        # Case 1.
        amount_total_orig_1 = self.sale_2.amount_total
        amount_total_expected = amount_total_orig_1 - discount_amount_2
        coupon_apply_wiz_2.with_context(active_id=self.sale_2.id).process_coupon()
        self.assertEqual(coupon.state, "used")
        self.assertEqual(self.sale_2.amount_total, amount_total_expected)
        consumption_line_so_2 = coupon.consumption_line_ids
        self.assertEqual(len(consumption_line_so_2), 0)  # single use
        # Case 2.
        amount_total_orig_1 = self.sale_2.amount_total
        amount_total_expected = 0
        self.coupon_apply_wiz.with_context(active_id=self.sale_2.id).process_coupon()
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        self.sale_2.action_confirm()
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        self.assertEqual(self.sale_2.amount_total, amount_total_expected)
        consumption_line_so_2 = self.coupon_multi_use_1.consumption_line_ids
        self.assertEqual(len(consumption_line_so_2), 1)
        self.assertEqual(consumption_line_so_2[0].amount, amount_total_orig_1)
        remaining_discount = DISCOUNT_AMOUNT - amount_total_orig_1
        # Delta showing left amount that can be consumed.
        self.assertEqual(
            self.coupon_multi_use_1.discount_fixed_amount_delta, remaining_discount
        )

    def test_06_coupon_multi_use(self):
        """Apply multi-use coupons, then cancel/draft/confirm SOs.

        Case 1: cancel sale orders.
        Case 2: set draft sale orders.
        """
        self.coupon_apply_wiz.with_context(active_id=self.sale_2.id).process_coupon()
        self.coupon_apply_wiz.with_context(active_id=self.sale_1.id).process_coupon()
        # Case 1.
        self.assertEqual(self.coupon_multi_use_1.state, "used")
        self.assertEqual(len(self.coupon_multi_use_1.consumption_line_ids), 2)
        self.sale_2.action_cancel()
        self.assertFalse(self.sale_2.coupon_multi_use_ids)
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        self.assertEqual(len(self.coupon_multi_use_1.consumption_line_ids), 1)
        self.sale_1.action_cancel()
        self.assertFalse(self.sale_1.coupon_multi_use_ids)
        self.assertFalse(self.coupon_multi_use_1.consumption_line_ids)
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        # Case 2.
        self.sale_2.action_draft()
        self.assertFalse(self.sale_2.coupon_multi_use_ids)
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        self.assertFalse(self.coupon_multi_use_1.consumption_line_ids)
        self.sale_1.action_draft()
        self.assertFalse(self.sale_1.coupon_multi_use_ids)
        self.assertEqual(self.coupon_multi_use_1.state, "new")
        self.assertFalse(self.coupon_multi_use_1.consumption_line_ids)
        self.assertFalse(self.sale_1.coupon_multi_use_ids)

    def test_07_coupon_multi_use(self):
        """Try to use different multi-use coupons from same program."""
        self.coupon_generate_wiz.generate_coupon()
        coupon_multi_use_2 = self.program_multi_use.coupon_ids[-1]
        # Apply first coupon
        self.coupon_apply_wiz.with_context(active_id=self.sale_1.id).process_coupon()
        # Imitate case when applied_coupon_ids is cleared by other SO.
        self.sale_2.applied_coupon_ids = [(4, self.coupon_multi_use_1.id)]
        # Try to apply second coupon from same program.
        with self.assertRaises(UserError):
            self.coupon_apply_wiz.coupon_code = coupon_multi_use_2.code
            self.coupon_apply_wiz.with_context(
                active_id=self.sale_1.id
            ).process_coupon()

    def _raise_multi_use_constraints(self, program):
        """Expect to raise exceptions when multi use coupons are used.

        Constraints are those where values can't be changed if
        coupon_multi_use=True, regardless if there are any coupons
        generated.

        Case 1: try to change discount type.
        Case 2: try to change reward type.
        Case 3: try to change program type.
        """
        # Case 1.
        with self.assertRaises(ValidationError):
            program.discount_type = "percentage"
        # Case 2.
        with self.assertRaises(ValidationError):
            program.reward_type = "product"
        # Case 3.
        with self.assertRaises(ValidationError):
            self.program_multi_use.program_type = "promotion_program"

    def _not_raise_multi_use_constraints(self, program):
        """Expect not to raise exceptions.

        Case 1: change discount type.
        Case 2: change reward type.
        Case 3: change program type.
        """
        try:
            # Case 1.
            program.discount_type = "percentage"
            # Case 2.
            program.reward_type = "product"
            # Case 3.
            program.program_type = "promotion_program"
        except ValidationError:
            self.fail(
                "Multi Use exceptions must not trigger if "
                "coupon_multi_use=False and no multi_use coupons generated."
            )

    def test_08_unlink_consumption_line(self):
        """Check if consumption line not allowed to unlink."""
        sale = self.sale_2
        # Apply a coupon to have consumption lines
        self.coupon_apply_wiz.with_context(active_id=sale.id).process_coupon()
        self.assertEqual(len(self.coupon_multi_use_1.consumption_line_ids), 1)
        # Test with not system user => access error
        with self.assertRaises(AccessError):
            user_admin = self.env.ref("base.user_admin")
            self.coupon_multi_use_1.sudo(user_admin).consumption_line_ids.unlink()
        # Test with remove reward line into sale order
        self.assertEqual(
            sale.order_line[2].product_id,
            self.program_multi_use.discount_line_product_id,
        )
        sale.write({"order_line": [(3, sale.order_line[2].id)]})
        self.assertEqual(len(self.coupon_multi_use_1.consumption_line_ids), 0)
        # Test with cancel sale order
        self.coupon_apply_wiz.with_context(active_id=sale.id).process_coupon()
        self.assertEqual(len(self.coupon_multi_use_1.consumption_line_ids), 1)
        sale.action_cancel()
        self.assertEqual(len(self.coupon_multi_use_1.consumption_line_ids), 0)

    def test_09_coupon_program_constraints(self):
        """Check coupon constraints when multi use coupon is generated."""
        with self.assertRaises(ValidationError) as error:
            self.program_multi_use.coupon_multi_use = False
        self.assertTrue(
            "Coupon multi use can't be changed with existing coupons."
            in error.exception.name
        )
        with self.assertRaises(ValidationError) as error:
            self.program_multi_use.discount_fixed_amount = 3000
        self.assertTrue(
            "Fixed Amount can't be changed when "
            "there are Multi Use coupons already." in error.exception.name
        )
        self._raise_multi_use_constraints(self.program_multi_use)

    def test_10_coupon_program_constraints(self):
        """Check constraints when multi use coupon is not generated.

        Case 1: multi_use=True
        Case 2: multi_use=False
        """

        def pass_discount_fixed_amount(program):
            fail_msg = (
                "There are no multi use coupons generated, so must be able"
                " to change discount_fixed_amount."
            )
            try:
                program.discount_fixed_amount = 3000
            except ValidationError:
                self.fail(fail_msg)

        # Copy program, so it would not have coupons.
        program = self.program_multi_use.copy()
        # Case 1.
        pass_discount_fixed_amount(program)
        self._raise_multi_use_constraints(program)
        # Case 2.
        program.coupon_multi_use = False
        pass_discount_fixed_amount(program)
        self._not_raise_multi_use_constraints(program)

    def test_11_coupon_program_constraints(self):
        """Try to use coupon_multi_use, when other options are incorrect."""
        with self.assertRaises(ValidationError):
            self.program_coupon_percentage.coupon_multi_use = True

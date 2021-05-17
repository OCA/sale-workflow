# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import float_compare

VALID_COUPON_CODE = "ELDONGHUT"
FIXED_AMOUNT_CODE = "FIXEDAMOUNT"


class AbstractCommonPromotionCase(object):
    def _get_promotion_rule_coupon_values(self):
        return {
            "name": "Best Promo",
            "code": VALID_COUPON_CODE,
            "rule_type": "coupon",
            "promo_type": "discount",
            "discount_amount": 20.00,
            "discount_type": "percentage",
            "minimal_amount": 50.00,
            "is_minimal_amount_tax_incl": False,
            "multi_rule_strategy": "use_best",
        }

    def _get_promotion_rule_auto_values(self):
        return {
            "name": "Best Promo Automatic",
            "rule_type": "auto",
            "promo_type": "discount",
            "discount_amount": 10.00,
            "discount_type": "percentage",
            "minimal_amount": 50.00,
            "is_minimal_amount_tax_incl": True,
            "multi_rule_strategy": "use_best",
        }

    def _get_promotion_rule_fixed_amount_values(self):
        return {
            "name": "Fixed amount promo",
            "code": FIXED_AMOUNT_CODE,
            "rule_type": "coupon",
            "promo_type": "discount",
            "discount_amount": 20.00,
            "discount_type": "amount_tax_excluded",
            "discount_product_id": self.discount_product_id.id,
            "discount_amount_currency_id": self.env.user.company_id.currency_id.id,
            "minimal_amount": 50.00,
            "multi_rule_strategy": "use_best",
        }

    def set_up(self, sale_xml_id):
        self.sale = self.env.ref(sale_xml_id)
        self.price_precision_digits = self.env["decimal.precision"].precision_get(
            "Product Price"
        )
        self.sale_promotion_rule = self.env["sale.promotion.rule"]
        self.discount_product_id = self.env.ref("sale_promotion_rule.coupon")
        data_coupon = self._get_promotion_rule_coupon_values()
        self.promotion_rule_coupon = self.sale_promotion_rule.search(
            [("name", "=", data_coupon["name"])]
        )
        if not self.promotion_rule_coupon:
            self.promotion_rule_coupon = self.sale_promotion_rule.create(data_coupon)
        data_auto = self._get_promotion_rule_auto_values()
        self.promotion_rule_auto = self.sale_promotion_rule.search(
            [("name", "=", data_auto["name"])]
        )
        if not self.promotion_rule_auto:
            self.promotion_rule_auto = self.sale_promotion_rule.create(data_auto)
        data_fixed_amount = self._get_promotion_rule_fixed_amount_values()
        self.promotion_rule_fixed_amount = self.sale_promotion_rule.search(
            [("name", "=", data_fixed_amount["name"])]
        )
        if not self.promotion_rule_fixed_amount:
            self.promotion_rule_fixed_amount = self.sale_promotion_rule.create(
                data_fixed_amount
            )

        self.tax_include_21 = self.env["account.tax"].create(
            dict(
                name="Include tax 21",
                amount="21.00",
                price_include=True,
                type_tax_use="sale",
            )
        )
        self.tax_include_5 = self.env["account.tax"].create(
            dict(
                name="Include tax 5",
                amount="5.00",
                price_include=True,
                type_tax_use="sale",
            )
        )
        self.tax_exclude_21 = self.env["account.tax"].create(
            dict(
                name="Exclude tax 21",
                amount="21.00",
                price_include=False,
                type_tax_use="sale",
            )
        )
        self.tax_exclude_5 = self.env["account.tax"].create(
            dict(
                name="Exclude tax 5",
                amount="5.00",
                price_include=False,
                type_tax_use="sale",
            )
        )
        # add a tax on our discount product
        self.discount_product_id.taxes_id = [(6, 0, [self.tax_exclude_21.id])]

    def add_coupon_code(self, coupon_code):
        self.sale.add_coupon(coupon_code)

    def check_discount_rule_set(self, line, promo_rule):
        if promo_rule.rule_type == "coupon":
            self.assertEqual(line.coupon_promotion_rule_id, promo_rule)
        else:
            self.assertEqual(line.promotion_rule_ids, promo_rule)
        self.assertEqual(line.discount, promo_rule.discount_amount)


class PromotionCase(TransactionCase, AbstractCommonPromotionCase):
    def setUp(self, *args, **kwargs):
        super(PromotionCase, self).setUp(*args, **kwargs)
        self.set_up("sale_promotion_rule.sale_order_promotion")

    def test_name_get(self):
        name = self.promotion_rule_auto.name_get()[0][1]
        self.assertTrue(name.endswith("(Automatic)"))
        name = self.promotion_rule_coupon.name_get()[0][1]
        self.assertTrue(name.startswith(self.promotion_rule_coupon.name))

    def test_add_valid_discount_code_for_all_line(self):
        self.add_coupon_code(VALID_COUPON_CODE)
        for line in self.sale.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

    def test_add_valid_discount_code_for_one_line(self):
        first_line = self.sale.order_line[0]
        first_line.discount = 20
        # we configure the list to specify that we want to keep the existing
        # disount if one is already specified
        self.promotion_rule_coupon.multi_rule_strategy = "keep_existing"
        self.promotion_rule_auto.multi_rule_strategy = "keep_existing"
        self.add_coupon_code(VALID_COUPON_CODE)
        self.assertEqual(first_line.discount, 20)
        self.assertEqual(first_line.coupon_promotion_rule_id.id, False)
        for line in self.sale.order_line[1:]:
            # The coupon are always applied first.
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

    def test_add_bad_discount_code(self):
        with self.assertRaises(UserError):
            self.add_coupon_code("DGRVBYTHT")

    def test_add_automatic_discount_code(self):
        self.sale.apply_promotions()
        for line in self.sale.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_auto)

    def test_use_best_discount(self):
        first_line = self.sale.order_line[0]
        first_line.discount = 5
        self.sale.apply_promotions()
        self.assertEqual(first_line.discount, 10)
        for line in self.sale.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_auto)
        self.add_coupon_code(VALID_COUPON_CODE)
        self.assertEqual(first_line.discount, 20)
        for line in self.sale.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

    def test_exclusive_rule(self):
        self.promotion_rule_coupon.multi_rule_strategy = "exclusive"
        self.promotion_rule_coupon.sequence = 10
        self.promotion_rule_auto.multi_rule_strategy = "exclusive"
        self.promotion_rule_auto.sequence = 20
        self.add_coupon_code(VALID_COUPON_CODE)
        self.sale.apply_promotions()
        self.assertEqual(
            self.promotion_rule_coupon, self.sale.applied_promotion_rule_ids
        )
        self.sale.clear_promotions()
        self.promotion_rule_coupon.sequence = 20
        self.promotion_rule_auto.sequence = 10
        self.add_coupon_code(VALID_COUPON_CODE)
        self.sale.apply_promotions()
        # coupon is always on top of applied promotion rules
        self.assertEqual(
            self.promotion_rule_coupon, self.sale.applied_promotion_rule_ids
        )

    def test_usage_restriction(self):
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        self.promotion_rule_coupon.usage_restriction = "one_per_partner"
        self.promotion_rule_coupon.multi_rule_strategy = "exclusive"
        self.promotion_rule_coupon.sequence = 10
        self.add_coupon_code(VALID_COUPON_CODE)
        self.sale.apply_promotions()
        self.assertIn(self.promotion_rule_coupon, self.sale.applied_promotion_rule_ids)
        # If create a new sale order for the same partner, the same promotion
        # rule can't be used
        new_sale = self.sale.copy()
        new_sale.add_coupon(VALID_COUPON_CODE)
        new_sale.apply_promotions()
        self.assertNotIn(
            self.promotion_rule_coupon, new_sale.applied_promotion_rule_ids
        )
        # if we change the usage restriction the promotion can be applied
        self.promotion_rule_coupon.usage_restriction = "no_restriction"
        new_sale = self.sale.copy()
        new_sale.add_coupon(VALID_COUPON_CODE)
        new_sale.apply_promotions()
        self.assertIn(self.promotion_rule_coupon, new_sale.applied_promotion_rule_ids)

    def test_discount_amount_product_constrains(self):
        with self.assertRaises(ValidationError):
            self.promotion_rule_fixed_amount.discount_product_id = False

    def test_discount_amount_untaxed(self):
        """Test with line where the tax is excluded from the price"""
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        self.promotion_rule_fixed_amount.discount_type = "amount_tax_excluded"
        # we force a tax on a line to be sure that we have a tax applied on
        # a line
        so_line = self.sale.order_line[0]
        so_line.product_id.taxes_id = [(6, 0, [self.tax_exclude_21.id])]
        so_line.product_id_change()
        amount_untaxed = self.sale.amount_untaxed
        # we apply a discount of 20 on untaxed amount
        self.add_coupon_code(FIXED_AMOUNT_CODE)
        new_amount = amount_untaxed - self.sale.amount_untaxed
        self.assertEqual(
            0,
            float_compare(
                new_amount,
                self.env.user.company_id.currency_id._convert(
                    20, self.sale.currency_id, self.sale.company_id, fields.Date.today()
                ),
                precision_digits=self.price_precision_digits,
            ),
            "%s != 20" % (new_amount),
        )

    def test_discount_amount_untaxed_2(self):
        """Test with line where the tax is included into the price"""
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        self.promotion_rule_fixed_amount.discount_type = "amount_tax_excluded"
        # we force a tax on a line to be sure that we have a tax applied on
        # a line
        so_line = self.sale.order_line[0]
        so_line.product_id.taxes_id = [(6, 0, [self.tax_include_21.id])]
        so_line.product_id_change()
        amount_untaxed = self.sale.amount_untaxed
        # we apply a discount of 20 on untaxed amount
        self.add_coupon_code(FIXED_AMOUNT_CODE)
        new_amount = amount_untaxed - self.sale.amount_untaxed
        self.assertEqual(
            0,
            float_compare(
                new_amount,
                self.env.user.company_id.currency_id._convert(
                    20, self.sale.currency_id, self.sale.company_id, fields.Date.today()
                ),
                precision_digits=self.price_precision_digits,
            ),
            "%s != 20" % (new_amount),
        )

    def test_discount_amount_taxed(self):
        """Test with line where the tax is excluded from the price"""
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        # add a tax in the prodduct
        so_line = self.sale.order_line[0]
        so_line.product_id.taxes_id = [(6, 0, [self.tax_exclude_21.id])]
        so_line.product_id_change()
        so_line = self.sale.order_line[1]
        so_line.product_id.taxes_id = [(6, 0, [self.tax_exclude_5.id])]
        so_line.product_id_change()
        self.promotion_rule_fixed_amount.discount_type = "amount_tax_included"
        amount_total = self.sale.amount_total
        # we apply a discount of 20 on amount taxed
        self.add_coupon_code(FIXED_AMOUNT_CODE)
        new_amount = amount_total - self.sale.amount_total
        self.assertEqual(
            0,
            float_compare(
                new_amount,
                self.env.user.company_id.currency_id._convert(
                    20, self.sale.currency_id, self.sale.company_id, fields.Date.today()
                ),
                precision_digits=self.price_precision_digits,
            ),
            "%s != 20" % (new_amount),
        )

    def test_discount_amount_taxed_2(self):
        """Test with line where the tax is included into the price"""
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        # add a tax in the prodduct
        so_line = self.sale.order_line[0]
        so_line.product_id.taxes_id = [(6, 0, [self.tax_include_21.id])]
        so_line.product_id_change()
        so_line = self.sale.order_line[1]
        so_line.product_id.taxes_id = [(6, 0, [self.tax_include_5.id])]
        so_line.product_id_change()
        self.promotion_rule_fixed_amount.discount_type = "amount_tax_included"
        amount_total = self.sale.amount_total
        # we apply a discount of 20 on amount taxed
        self.add_coupon_code(FIXED_AMOUNT_CODE)
        new_amount = amount_total - self.sale.amount_total
        self.assertEqual(
            0,
            float_compare(
                new_amount,
                self.env.user.company_id.currency_id._convert(
                    20, self.sale.currency_id, self.sale.company_id, fields.Date.today()
                ),
                precision_digits=self.price_precision_digits,
            ),
            "%s != 20" % (new_amount),
        )

    def test_discount_amount_rounding(self):
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        # add a tax in the prodduct and special price
        so_line = self.sale.order_line[0]
        so_line.product_id.taxes_id = [(6, 0, [self.tax_exclude_21.id])]
        so_line.product_id_change()
        so_line.price_unit = 719.77
        so_line = self.sale.order_line[1]
        so_line.product_id.taxes_id = [(6, 0, [self.tax_exclude_5.id])]
        so_line.product_id_change()
        so_line.price_unit = 13.66
        self.promotion_rule_fixed_amount.discount_type = "amount_tax_included"
        discount_amount = 3.00
        self.promotion_rule_fixed_amount.discount_amount = discount_amount
        amount_total = self.sale.amount_total
        # we apply a discount of 8 on amount taxed
        self.add_coupon_code(FIXED_AMOUNT_CODE)
        new_amount = amount_total - self.sale.amount_total
        self.assertEqual(
            0,
            float_compare(
                new_amount,
                self.env.user.company_id.currency_id._convert(
                    discount_amount,
                    self.sale.currency_id,
                    self.sale.company_id,
                    fields.Date.today(),
                ),
                precision_digits=self.price_precision_digits,
            ),
            "{} != {}".format(new_amount, discount_amount),
        )

    def test_discount_amount_rounding_2(self):
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        # here we test with a large SO and price with large difference
        for price in [5.65, 77.68, 51.07, 87.09, 29.31, 61.03, 99.89, 54.32, 44.95]:
            so_line = self.sale.order_line[1].copy({"order_id": self.sale.id})
            so_line.product_id.taxes_id = [(6, 0, [self.tax_exclude_21.id])]
            so_line.product_id_change()
            so_line.price_unit = price
        for price in [
            485.75,
            376.83,
            221.52,
            394.26,
            294.47,
            261.01,
            385.64,
            288.74,
            150.84,
        ]:
            so_line = self.sale.order_line[1].copy({"order_id": self.sale.id})
            so_line.product_id.taxes_id = [(6, 0, [self.tax_include_21.id])]
            so_line.product_id_change()
            so_line.price_unit = price
        for price in [
            798.33,
            546.82,
            966.38,
            760.5,
            835.4,
            808.44,
            586.81,
            738.34,
            558.55,
        ]:
            so_line = self.sale.order_line[1].copy({"order_id": self.sale.id})
            so_line.product_id.taxes_id = [(6, 0, [self.tax_exclude_5.id])]
            so_line.product_id_change()
            so_line.price_unit = price
        for discount_amount in range(0, 20, 3):
            self.promotion_rule_fixed_amount.discount_type = "amount_tax_included"
            self.promotion_rule_fixed_amount.discount_amount = discount_amount
            amount_total = self.sale.amount_total
            self.add_coupon_code(FIXED_AMOUNT_CODE)
            new_amount = amount_total - self.sale.amount_total
            price = self.env.user.company_id.currency_id._convert(
                from_amount=discount_amount,
                to_currency=self.sale.currency_id,
                company=self.sale.company_id,
                date=datetime.date.today(),
            )

            self.assertEqual(
                0,
                float_compare(
                    new_amount,
                    price,
                    precision_digits=self.price_precision_digits,
                ),
                "{} != {}".format(new_amount, price),
            )
            self.sale.clear_promotions()

    def test_multi_promotion_rules(self):
        """
        Ensure it's working in case of multi available promotions.
        So the first promotion rule (promotion_rule_auto) should be check
        (and not available due to minimal amount), then the promo_copy should
        be check and applied.
        :return:
        """
        promo_copy = self.promotion_rule_auto.copy({"name": "Almost free"})
        self.promotion_rule_auto.write({"minimal_amount": 999999})
        self.sale.apply_promotions()
        for line in self.sale.order_line:
            self.check_discount_rule_set(line, promo_copy)
        return

    def test_promotion_fixed_plus_discount(self):
        """
        Apply a manual discount on a line and apply a coupon code with
        fixed amount and combine strategy. Both should apply.
        """
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        self.promotion_rule_fixed_amount.discount_type = "amount_tax_included"
        self.promotion_rule_fixed_amount.multi_rule_strategy = "cumulate"
        so_line = self.sale.order_line[0]
        so_line.discount = 20.0
        so_line.price_unit = 80.0
        amount = self.sale.amount_total
        # self.sale.amount_total = 710
        self.assertEqual(710, self.sale.amount_total)
        self.add_coupon_code(FIXED_AMOUNT_CODE)
        self.sale.apply_promotions()
        self.assertEqual(
            20,
            so_line.discount,
        )
        amount_discount = amount - self.sale.amount_total
        # self.sale.amount_total = 694
        self.assertEqual(
            0,
            float_compare(
                amount_discount,
                self.env.user.company_id.currency_id._convert(
                    so_line.discount,
                    self.sale.currency_id,
                    self.sale.company_id,
                    fields.Date.today(),
                ),
                precision_digits=self.price_precision_digits,
            ),
            "{} != {}".format(amount_discount, so_line.discount),
        )
        self.assertFalse(so_line.coupon_promotion_rule_id)

    def test_multi_promotion_rules_exclusive_sequence(self):
        """
        Ensure it's working in case of multi available promotions.
        So the first promotion rule > 100 should not be applied
        :return:
        """
        promo_copy = self.promotion_rule_auto.copy(
            {
                "name": "> 100",
                "minimal_amount": 199,
                "multi_rule_strategy": "exclusive",
                "sequence": 10,
            }
        )
        self.promotion_rule_auto.write(
            {"minimal_amount": 100, "multi_rule_strategy": "exclusive", "sequence": 20}
        )
        self.sale.apply_promotions()
        for line in self.sale.order_line:
            self.check_discount_rule_set(line, promo_copy)
        return


class CurrencyPromotionCase(TransactionCase, AbstractCommonPromotionCase):
    def setUp(self, *args, **kwargs):
        super(CurrencyPromotionCase, self).setUp(*args, **kwargs)
        self.set_up("sale.sale_order_3")

    def test_discount_amount_rounding_currency(self):
        """
        Test a sale order in different currency
        Remove all taxes - no sense in that case
        """
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        self.discount_product_id.taxes_id = False
        # here we test with a large SO and price with large difference
        for price in [5.65, 77.68, 51.07, 87.09, 29.31, 61.03, 99.89, 54.32, 44.95]:
            so_line = self.sale.order_line[1].copy({"order_id": self.sale.id})
            so_line.product_id.taxes_id = False
            so_line.product_id_change()
            so_line.price_unit = price
        for price in [
            485.75,
            376.83,
            221.52,
            394.26,
            294.47,
            261.01,
            385.64,
            288.74,
            150.84,
        ]:
            so_line = self.sale.order_line[1].copy({"order_id": self.sale.id})
            so_line.product_id.taxes_id = False
            so_line.product_id_change()
            so_line.price_unit = price
        for price in [
            798.33,
            546.82,
            966.38,
            760.5,
            835.4,
            808.44,
            586.81,
            738.34,
            558.55,
        ]:
            so_line = self.sale.order_line[1].copy({"order_id": self.sale.id})
            so_line.product_id.taxes_id = False
            so_line.product_id_change()
            so_line.price_unit = price
        for discount_amount in range(0, 20, 3):
            self.promotion_rule_fixed_amount.discount_type = "amount_tax_included"
            self.promotion_rule_fixed_amount.discount_amount = discount_amount
            amount_total = self.sale.amount_total
            self.add_coupon_code(FIXED_AMOUNT_CODE)
            new_amount = amount_total - self.sale.amount_total
            price = self.env.user.company_id.currency_id._convert(
                from_amount=discount_amount,
                to_currency=self.sale.currency_id,
                company=self.sale.company_id,
                date=datetime.date.today(),
            )

            self.assertEqual(
                0,
                float_compare(
                    new_amount,
                    price,
                    precision_digits=self.price_precision_digits,
                ),
                "{} != {}".format(new_amount, price),
            )
            self.sale.clear_promotions()

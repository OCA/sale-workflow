# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tools import float_compare

VALID_COUPON_CODE = "ELDONGHUT"


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
            "multi_rule_strategy": "use_best"
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
            "multi_rule_strategy": "use_best"
        }

    def set_up(self, sale_xml_id):
        self.sale = self.env.ref(sale_xml_id)
        self.price_precision_digits = self.env[
            'decimal.precision'].precision_get('Product Price')
        self.sale_promotion_rule = self.env["sale.promotion.rule"]
        data_coupon = self._get_promotion_rule_coupon_values()
        self.promotion_rule_coupon = self.sale_promotion_rule.search([
            ("name", "=", data_coupon["name"])
        ])
        if not self.promotion_rule_coupon:
            self.promotion_rule_coupon = self.sale_promotion_rule.create(
                data_coupon
            )
        data_auto = self._get_promotion_rule_auto_values()
        self.promotion_rule_auto = self.sale_promotion_rule.search([
            ("name", "=", data_auto["name"])
        ])
        if not self.promotion_rule_auto:
            self.promotion_rule_auto = self.sale_promotion_rule.create(
                data_auto
            )

    def add_coupon_code(self, coupon_code):
        self.sale.add_coupon(coupon_code)

    def check_discount_rule_set(self, line, promo_rule):
        if promo_rule.rule_type == 'coupon':
            self.assertEqual(line.coupon_promotion_rule_id, promo_rule)
        else:
            self.assertEqual(line.promotion_rule_ids, promo_rule)
        self.assertEqual(line.discount, promo_rule.discount_amount)


class PromotionCase(TransactionCase, AbstractCommonPromotionCase):

    def setUp(self, *args, **kwargs):
        super(PromotionCase, self).setUp(*args, **kwargs)
        self.set_up('sale.sale_order_3')

    def test_add_valid_discount_code_for_all_line(self):
        self.add_coupon_code(VALID_COUPON_CODE)
        for line in self.sale.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

    def test_add_valid_discount_code_for_one_line(self):
        first_line = self.sale.order_line[0]
        first_line.discount = 20
        # we configure the list to specify that we want to keep the existing
        # disount if one is already specified
        self.promotion_rule_coupon.multi_rule_strategy = 'keep_existing'
        self.promotion_rule_auto.multi_rule_strategy = 'keep_existing'
        self.add_coupon_code(VALID_COUPON_CODE)
        self.assertEqual(first_line.discount, 20)
        self.assertEqual(first_line.coupon_promotion_rule_id.id, False)
        for line in self.sale.order_line[1:]:
            # The coupon are always applied first.
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

    def test_add_bad_discount_code(self):
        with self.assertRaises(UserError):
            self.add_coupon_code('DGRVBYTHT')

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
        self.add_coupon_code('ELDONGHUT')
        self.sale.apply_promotions()
        self.assertEqual(
            self.promotion_rule_coupon, self.sale.applied_promotion_rule_ids
        )
        self.sale.clear_promotions()
        self.promotion_rule_coupon.sequence = 20
        self.promotion_rule_auto.sequence = 10
        self.add_coupon_code('ELDONGHUT')
        self.sale.apply_promotions()
        # coupon is always on top of applied promotion rules
        self.assertEqual(
            self.promotion_rule_coupon, self.sale.applied_promotion_rule_ids

    def test_discount_amount_untaxed(self):
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        self.promotion_rule_coupon.discount_type = "amount_tax_excluded"
        amount_untaxed = self.sale.amount_untaxed
        # we apply a discount of 20 on untaxed amount
        self.add_coupon_code("ELDONGHUT")
        new_amount = amount_untaxed - self.sale.amount_untaxed
        self.assertEqual(
            0,
            float_compare(
                new_amount,
                20,
                precision_digits=self.price_precision_digits
            )
        )

    def test_discount_amount_taxed(self):
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        # add a tax in the prodduct
        tax_include_id = self.env['account.tax'].create(
            dict(name="Include tax 21",
                 amount='21.00',
                 price_include=True,
                 type_tax_use='sale'))
        so_line = self.sale.order_line[0]
        so_line.product_id.taxes_id = [(6, 0, [tax_include_id.id])]
        so_line.product_id_change()
        tax_include_id = self.env['account.tax'].create(
            dict(name="Include tax 5",
                 amount='5.00',
                 price_include=True,
                 type_tax_use='sale'))
        so_line = self.sale.order_line[1]
        so_line.product_id.taxes_id = [(6, 0, [tax_include_id.id])]
        so_line.product_id_change()
        self.promotion_rule_coupon.discount_type = "amount_tax_included"
        amount_total = self.sale.amount_total
        # we apply a discount of 20 on amount taxed
        self.add_coupon_code("ELDONGHUT")
        new_amount = amount_total - self.sale.amount_total
        self.assertEqual(
            0,
            float_compare(
                new_amount,
                20,
                precision_digits=self.price_precision_digits
            ),
            "%s != 20" % (new_amount)
        )

    def test_discount_amount_rounding(self):
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        # add a tax in the prodduct and special price
        so_line = self.sale.order_line[0]
        tax_include_id = self.env['account.tax'].create(
            dict(name="Include tax 21",
                 amount='21.00',
                 price_include=True,
                 type_tax_use='sale'))
        so_line.product_id.taxes_id = [(6, 0, [tax_include_id.id])]
        so_line.product_id_change()
        so_line.price_unit = 719.77
        so_line = self.sale.order_line[1]
        tax_include_id = self.env['account.tax'].create(
            dict(name="Include tax 5",
                 amount='5.00',
                 price_include=True,
                 type_tax_use='sale'))
        so_line.product_id.taxes_id = [(6, 0, [tax_include_id.id])]
        so_line.product_id_change()
        so_line.price_unit = 13.66
        self.promotion_rule_coupon.discount_type = "amount_tax_included"
        discount_amount = 3.00
        self.promotion_rule_coupon.discount_amount = discount_amount
        amount_total = self.sale.amount_total
        # we apply a discount of 8 on amount taxed
        self.add_coupon_code("ELDONGHUT")
        new_amount = amount_total - self.sale.amount_total
        self.assertEqual(
            0,
            float_compare(
                new_amount,
                discount_amount,
                precision_digits=self.price_precision_digits
            ),
            "%s != %s" % (new_amount, discount_amount)
        )

    def test_discount_amount_rounding_2(self):
        self.promotion_rule_auto.minimal_amount = 999999999  # disable
        # here we test with a large SO and price with large difference
        for i in range(1, 10):
            so_line = self.sale.order_line[1].copy({"order_id": self.sale.id})
            so_line.price_unit = random.uniform(1.05, 100.99)
        #for i in range(1, 10):
        #    so_line = self.sale.order_line[1].copy({"order_id": self.sale.id})
        #    so_line.price_unit = random.uniform(101.00, 500.99)
        #for i in range(1, 10):
        #    so_line = self.sale.order_line[1].copy({"order_id": self.sale.id})
        #    so_line.price_unit = random.uniform(500.99, 1000.00)

        for discount_amount in range(3, 30, 3):
            self.promotion_rule_coupon.discount_type = "amount_tax_included"
            self.promotion_rule_coupon.discount_amount = discount_amount
            amount_total = self.sale.amount_total
            # we apply a discount of 8 on amount taxed
            self.add_coupon_code("ELDONGHUT")
            new_amount = amount_total - self.sale.amount_total
            self.assertEqual(
                0,
                float_compare(
                    new_amount,
                    discount_amount,
                    precision_digits=self.price_precision_digits
                ),
                "%s != %s" % (new_amount, discount_amount)
            )
            self.sale.clear_promotions()

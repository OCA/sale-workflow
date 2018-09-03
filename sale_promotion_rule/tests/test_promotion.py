# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class AbstractCommonPromotionCase(object):

    def set_up(self, sale_xml_id):
        self.sale = self.env.ref(sale_xml_id)
        self.promotion_rule_coupon = self.env.ref(
            'sale_promotion_rule.rule_coupon')
        self.promotion_rule_auto = self.env.ref(
            'sale_promotion_rule.rule_auto')

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
        self.add_coupon_code('ELDONGHUT')
        for line in self.sale.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

    def test_add_valid_discount_code_for_one_line(self):
        first_line = self.sale.order_line[0]
        first_line.discount = 20
        # we configure the list to specify that we want to keep the existing
        # disount if one is already specified
        self.promotion_rule_coupon.multi_rule_strategy = 'keep_existing'
        self.promotion_rule_auto.multi_rule_strategy = 'keep_existing'
        self.add_coupon_code('ELDONGHUT')
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
        self.add_coupon_code('ELDONGHUT')
        self.assertEqual(first_line.discount, 20)
        for line in self.sale.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase

from odoo.addons.sale_promotion_rule.tests.test_promotion import (
    AbstractCommonPromotionCase,
)


class PromotionCase(TransactionCase, AbstractCommonPromotionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.normal_delivery = self.env.ref("delivery.normal_delivery_carrier")
        self.set_up("sale_promotion_rule.sale_order_promotion")
        self.sale.carrier_id = self.normal_delivery.id
        delivery_wizard = Form(
            self.env["choose.delivery.carrier"].with_context(
                {
                    "default_order_id": self.sale.id,
                    "default_carrier_id": self.sale.carrier_id,
                }
            )
        )
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.update_price()
        choose_delivery_carrier.button_confirm()
        self.delivery_lines = self.sale.order_line.filtered(lambda l: l.is_delivery)

    def assert_delivery_line_exists(self):
        self.assertTrue(self.delivery_lines)

    def test_discount_code_for_all_line_expect_delivery(self):
        self.assert_delivery_line_exists()
        self.add_coupon_code("ELDONGHUT")
        for line in self.sale.order_line:
            if line.is_delivery:
                self.assertFalse(line.applied_promotion_rule_ids)
            else:
                self.check_discount_rule_set(line, self.promotion_rule_coupon)

    def test_add_automatic_discount_except_delivery(self):
        self.assert_delivery_line_exists()
        self.sale.apply_promotions()
        for line in self.sale.order_line:
            if line.is_delivery:
                self.assertFalse(line.applied_promotion_rule_ids)
            else:
                self.check_discount_rule_set(line, self.promotion_rule_auto)

    def test_lines_excluded_from_total_amount(self):
        self.assert_delivery_line_exists()
        self.assertIn(
            self.delivery_lines,
            self.promotion_rule_coupon._get_lines_excluded_from_total_amount(self.sale),
        )

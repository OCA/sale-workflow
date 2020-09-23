# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon


# TODO: refactor test classes for better reusability
class TestProgramForNFirstSaleOrder(TestSaleCouponCommon):
    def _create_order(self, product, qty):
        order = self.empty_order

        order.write(
            {
                "order_line": [
                    (0, False, {"product_id": product.id, "product_uom_qty": qty})
                ]
            }
        )
        return order

    def setUp(self):
        super().setUp()
        self.env["sale.coupon.program"].search([]).write({"active": False})
        self.program = self.env["sale.coupon.program"].create(
            {
                "name": "Program",
                "promo_code_usage": "no_code_needed",
                "reward_type": "discount",
                "active": True,
                "discount_type": "percentage",
                "discount_percentage": 10.0,
            }
        )

    def test_01_no_n_orders(self):
        """`next_n_customer_orders` == 0, program applied always."""
        self.program.write({"next_n_customer_orders": 0})
        order = self._create_order(self.product_A, 1)
        order.recompute_coupon_lines()
        for __ in range(3):
            self.assertEqual(order.amount_untaxed, 90)
            order = order.copy()

    def test_02_max_2_orders(self):
        """`next_n_customer_orders` == 2, program applied 2 times."""
        max_orders = 2
        partner = self.env["res.partner"].create(
            {"name": "Test Partner", "is_company": True}
        )
        self.program.write({"next_n_customer_orders": max_orders})
        order = self._create_order(self.product_A, 1)
        # Create new order without coupon used.
        order_without_coupon = order.copy()
        self.assertEqual(order_without_coupon.amount_untaxed, 100)
        order.recompute_coupon_lines()  # used first time
        self.assertEqual(order.amount_untaxed, 90)
        # Create new order with coupon used, but with different partner.
        order_with_diff_partner = order.copy(default={"partner_id": partner.id})
        self.assertEqual(order_with_diff_partner.amount_untaxed, 90)
        self.assertEqual(order.amount_untaxed, 90)
        order = order.copy()  # used second time
        self.assertEqual(order.amount_untaxed, 90)
        order = order.copy()  # tried to use third time.
        self.assertEqual(order.amount_untaxed, 100)

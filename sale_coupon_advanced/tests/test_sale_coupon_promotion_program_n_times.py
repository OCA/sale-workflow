# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon


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

    def test_no_n_orders(self):
        """
        If `first_n_customer_orders` == 0, program is always appliable.
        """
        self.program.write({"first_n_customer_orders": 0})
        order = self._create_order(self.product_A, 1)
        order.recompute_coupon_lines()
        for __ in range(10):
            self.assertEqual(order.amount_untaxed, 90)
            order = order.copy()

    def test_max_2_orders(self):
        """
        If `first_n_customer_orders` > 0, program is appliable n times.
        """
        max_orders = 2
        self.program.write({"first_n_customer_orders": max_orders})
        order = self._create_order(self.product_A, 1)
        order.recompute_coupon_lines()
        for __ in range(max_orders):
            self.assertEqual(order.amount_untaxed, 90)
            order = order.copy()
        self.assertEqual(order.amount_untaxed, 100)

# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .common import TestSaleCoupon


class TestSaleCouponCumulative(TestSaleCoupon):
    def setUp(self):
        super().setUp()
        self.pricelist = self.env["product.pricelist"].create(
            {
                "name": "Promotion Pricelist",
                "active": False,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "compute_price": "fixed",
                            "fixed_price": 50.0,
                            "applied_on": "0_product_variant",
                            "product_id": self.product_D.id,
                        },
                    )
                ],
            }
        )

    def test_program_pricelist_applied(self):
        order = self._create_order()
        order.recompute_coupon_lines()
        sol_product_d = order.order_line.filtered(
            lambda line: line.product_id == self.product_D
        )
        self.assertEqual(sol_product_d.price_unit, 100.00)
        # update one program to use pricelist settings
        self.program_c.write(
            {"reward_pricelist_id": self.pricelist.id, "reward_type": "use_pricelist"}
        )
        order.recompute_coupon_lines()
        self.assertEqual(order.pricelist_id, self.pricelist)
        self.assertEqual(sol_product_d.price_unit, 50.00)

    def test_program_pricelist_rollbacked(self):
        self.program_c.write(
            {"reward_pricelist_id": self.pricelist.id, "reward_type": "use_pricelist"}
        )
        order = self._create_order()
        order.recompute_coupon_lines()
        sol_product_d = order.order_line.filtered(
            lambda line: line.product_id == self.product_D
        )
        self.assertEqual(sol_product_d.price_unit, 50.00)
        # disable program with pricelist
        self.program_c.active = False
        order.recompute_coupon_lines()
        self.assertNotEqual(order.pricelist_id, self.pricelist)
        self.assertEqual(sol_product_d.price_unit, 100.00)

from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon


class TestSaleCouponOrderDiscountFastChange(TestSaleCouponCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "list_price": 20.0,
                "taxes_id": False,
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "John Doe",
            }
        )

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

        cls.env["sale.order.line"].create(
            {
                "product_id": cls.product1.id,
                "name": "Product 1",
                "product_uom_qty": 2.0,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "order_id": cls.order.id,
            }
        )

        cls.env["coupon.program"].create(
            {
                "name": "10% on all orders",
                "promo_code_usage": "no_code_needed",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "program_type": "promotion_program",
            }
        )
        cls.order.recompute_coupon_lines()

    def test_01_apply_global_discount_on_reward_lines(self):
        self.assertEqual(self.order.amount_total, 36.0)
        wizard = self.env["sale.order.discount.fast.change"]
        wiz = wizard.create({})
        wiz = self.env["sale.order.discount.fast.change"].create(
            {
                "discount": 5.0,
                "application_policy": "all",
                "skip_reward_lines": False,
            }
        )
        wiz.with_context(active_id=self.order.id).apply_global_discount()
        self.assertEqual(self.order.amount_total, 34.2)  # 40 * 0.95 - 4 * 0.95

    def test_02_apply_global_discount_on_non_reward_lines(self):
        self.assertEqual(self.order.amount_total, 36.0)
        wizard = self.env["sale.order.discount.fast.change"]
        wiz = wizard.create({})
        wiz = self.env["sale.order.discount.fast.change"].create(
            {
                "discount": 5.0,
                "application_policy": "not_discounted",
                "skip_reward_lines": True,
            }
        )
        wiz.with_context(active_id=self.order.id).apply_global_discount()
        self.assertEqual(self.order.amount_total, 34.0)  # 40 * 0.95 - 4

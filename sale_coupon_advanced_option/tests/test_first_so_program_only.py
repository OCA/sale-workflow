from odoo.exceptions import UserError

from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon


class TestProgramForFirstSaleOrder(TestSaleCouponCommon):
    def setUp(self):
        super(TestProgramForFirstSaleOrder, self).setUp()

        self.env["sale.coupon.program"].search([]).write({"active": False})

        self.product_A = self.env["product.product"].create(
            {"name": "Product A", "list_price": 60, "sale_ok": True}
        )

        self.program1 = self.env["sale.coupon.program"].create(
            {
                "name": "Get 10% discount for 1st order",
                "program_type": "promotion_program",
                "reward_type": "discount",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "rule_min_quantity": 1,
                "rule_minimum_amount": 100.00,
                "promo_applicability": "on_current_order",
                "promo_code_usage": "no_code_needed",
                "maximum_use_number": 0,
                "first_order_only": True,
                "active": True,
            }
        )

        self.program2 = self.env["sale.coupon.program"].create(
            {
                "name": "Get 50% discount",
                "program_type": "promotion_program",
                "reward_type": "discount",
                "discount_type": "percentage",
                "discount_percentage": 50.0,
                "rule_min_quantity": 1,
                "rule_minimum_amount": 100.00,
                "promo_applicability": "on_current_order",
                "promo_code_usage": "no_code_needed",
                "maximum_use_number": 0,
                "active": False,
            }
        )

        self.program3 = self.env["sale.coupon.program"].create(
            {
                "name": "Get 30% discount with code",
                "program_type": "promotion_program",
                "reward_type": "discount",
                "discount_type": "percentage",
                "discount_percentage": 30.0,
                "rule_min_quantity": 1,
                "rule_minimum_amount": 100.00,
                "promo_applicability": "on_current_order",
                "promo_code_usage": "code_needed",
                "promo_code": "30_discount",
                "maximum_use_number": 0,
                "first_order_only": True,
                "active": True,
            }
        )

        self.partner1 = self.env["res.partner"].create({"name": "Jane Doe"})

        self.partner2 = self.env["res.partner"].create({"name": "John Doe"})

        self.partner3 = self.env["res.partner"].create({"name": "John Deere"})

    def test_first_sale_order_program(self):

        #  test first sale order program

        order1 = self.env["sale.order"].create({"partner_id": self.partner1.id})
        order1.write(
            {
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_A.id,
                            "name": "Product A",
                            "product_uom_qty": 2.0,
                            "product_uom": self.uom_unit.id,
                        },
                    ),
                ]
            }
        )

        order1.recompute_coupon_lines()
        discounts = set(order1.order_line.mapped("name")) - {"Product A"}
        self.assertEqual(len(discounts), 1, "Order should contain one discount")
        self.assertTrue(
            "Get 10% discount for 1st order" in discounts.pop(),
            "The discount should be a 10% discount",
        )
        self.assertEqual(
            len(order1.order_line.ids), 2, "The order should contain 2 lines"
        )

        #  test non first sale order

        order2 = self.env["sale.order"].create({"partner_id": self.partner1.id})
        order2.write(
            {
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_A.id,
                            "name": "Product A",
                            "product_uom_qty": 3.0,
                            "product_uom": self.uom_unit.id,
                        },
                    ),
                ]
            }
        )

        order2.recompute_coupon_lines()
        self.assertEqual(
            len(order2.order_line.ids), 1, "The order should contain 1 line"
        )
        discounts = set(order2.order_line.mapped("name")) - {"Product A"}
        self.assertEqual(len(discounts), 0, "Order should contain no discount")

        self.program2.write({"active": True})
        order2.recompute_coupon_lines()
        self.assertEqual(
            len(order2.order_line.ids), 2, "The order should contain 2 lines"
        )
        discounts = set(order2.order_line.mapped("name")) - {
            "Product A"
        }  # to check by content of name that 2nd program was applied
        self.assertEqual(len(discounts), 1, "Order should contain 1 discount")
        self.assertTrue(
            "Get 50% discount" in discounts.pop(),
            "The discount should be a 50% discount",
        )

        # test first sale order another partner

        order3 = self.env["sale.order"].create({"partner_id": self.partner2.id})

        order3.write(
            {
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_A.id,
                            "name": "Product A",
                            "product_uom_qty": 3.0,
                            "product_uom": self.uom_unit.id,
                        },
                    ),
                ]
            }
        )

        order3.recompute_coupon_lines()
        discounts = set(order3.order_line.mapped("name")) - {"Product A"}

        self.assertEqual(
            len(order3.order_line.ids), 2, "The order should contain 2 lines"
        )
        self.assertEqual(
            len(discounts),
            1,
            "the order should contain 1 Product A line and a discount",
        )

        # test first sale order with promo code

        self.env["sale.coupon.generate"].with_context(
            active_id=self.program3.id
        ).create({"generation_type": "nbr_coupon", "nbr_coupons": 1}).generate_coupon()

        order4 = self.env["sale.order"].create({"partner_id": self.partner3.id})

        order4.write(
            {
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_A.id,
                            "name": "Product A",
                            "product_uom_qty": 2.0,
                            "product_uom": self.uom_unit.id,
                        },
                    ),
                ]
            }
        )

        self.env["sale.coupon.apply.code"].with_context(active_id=order4.id).create(
            {"coupon_code": "30_discount"}
        ).process_coupon()

        discounts = set(order3.order_line.mapped("name")) - {"Product A"}

        self.assertEqual(
            len(order3.order_line.ids), 2, "The order should contain 2 lines"
        )
        self.assertEqual(
            len(discounts),
            1,
            "the order should contain 1 Product A line and a discount",
        )

        # next so for old partner with 1st SO only code usage

        order5 = self.env["sale.order"].create({"partner_id": self.partner3.id})

        order5.write(
            {
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_A.id,
                            "name": "Product A",
                            "product_uom_qty": 5.0,
                            "product_uom": self.uom_unit.id,
                        },
                    ),
                ]
            }
        )

        with self.assertRaises(UserError):
            self.env["sale.coupon.apply.code"].with_context(active_id=order5.id).create(
                {"coupon_code": "30_discount"}
            ).process_coupon()

        discounts = set(order5.order_line.mapped("name")) - {"Product A"}

        self.assertEqual(
            len(order5.order_line.ids), 1, "The order should contain 1 line"
        )
        self.assertEqual(
            len(discounts),
            0,
            "the order should contain 1 Product A line and no discounts",
        )

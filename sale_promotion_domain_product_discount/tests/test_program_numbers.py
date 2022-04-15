from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged("post_install", "-at_install")
class CetmixTestSaleCouponProgram(SavepointCase):
    def setUp(self):
        super(CetmixTestSaleCouponProgram, self).setUp()
        self.largeCabinet = self.env["product.product"].create(
            {
                "name": "Large Cabinet",
                "list_price": 50.0,
                "taxes_id": False,
            }
        )
        self.conferenceChair = self.env["product.product"].create(
            {
                "name": "Conference Chair",
                "list_price": 100,
                "taxes_id": False,
            }
        )
        self.pedalBin = self.env["product.product"].create(
            {
                "name": "Pedal Bin",
                "list_price": 150,
                "taxes_id": False,
            }
        )
        self.drawerBlack = self.env["product.product"].create(
            {
                "name": "Drawer Black",
                "list_price": 200,
                "taxes_id": False,
            }
        )
        self.steve = self.env["res.partner"].create(
            {
                "name": "Steve Bucknor",
                "email": "steve.bucknor@example.com",
            }
        )
        self.order = self.env["sale.order"].create({"partner_id": self.steve.id})
        # Add products in order
        self.large_cabinet_line = self.env["sale.order.line"].create(
            {
                "product_id": self.largeCabinet.id,
                "name": "Large Cabinet",
                "product_uom_qty": 7.0,
                "order_id": self.order.id,
            }
        )
        self.conference_chair_line = self.env["sale.order.line"].create(
            {
                "product_id": self.conferenceChair.id,
                "name": "Conference Chair",
                "product_uom_qty": 5.0,
                "order_id": self.order.id,
            }
        )
        self.pedal_bin_line = self.env["sale.order.line"].create(
            {
                "product_id": self.pedalBin.id,
                "name": "Pedal Bin",
                "product_uom_qty": 10.0,
                "order_id": self.order.id,
            }
        )
        self.drawer_black_line = self.env["sale.order.line"].create(
            {
                "product_id": self.drawerBlack.id,
                "name": "Drawer Black",
                "product_uom_qty": 2.0,
                "order_id": self.order.id,
            }
        )

    def test_program_reward_discount_line_domain_matching(self):
        """
        Test program with reward type is `discount_line` for domain matching of product
        """
        # Now we want to apply a 10% discount only on Large Cabinet and Pedal Bin
        self.env["coupon.program"].create(
            {
                "name": "10% reduction on Large Cabinet and Pedal Bin in cart",
                "promo_code_usage": "no_code_needed",
                "reward_type": "discount_line",
                "program_type": "promotion_program",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "rule_products_domain": "[('id', 'in', [%s, %s])]"
                % (self.largeCabinet.id, self.pedalBin.id),
                "active": True,
                "discount_apply_on": "domain_product",
            }
        )
        # Apply all the programs
        self.order.recompute_coupon_lines()
        # Check that Large Cabinet and Pedal Bin has discount after apply program
        self.assertEqual(
            self.large_cabinet_line.discount,
            10,
            "The discount for Large Cabinet should be 10%",
        )
        self.assertEqual(
            self.pedal_bin_line.discount, 10, "The discount for Pedal Bin should be 10%"
        )
        # Check that other products hasn't discount
        self.assertEqual(
            self.conference_chair_line.discount,
            0,
            "The discount for Conference Chair should be empty",
        )
        self.assertEqual(
            self.drawer_black_line.discount,
            0,
            "The discount for Drawer Black should be empty",
        )
        # Check amount total after apply coupon
        self.assertEqual(
            self.order.amount_total,
            2565.0,
            "The order total with programs should be 2565.00",
        )

    def test_program_reward_discount_line_specific_product(self):
        """
        Test program with reward type is `discount_line` for specific product
        """
        # Now we want to apply a 10% discount for specific product Drawer Black
        self.env["coupon.program"].create(
            {
                "name": "10% reduction for specific product",
                "promo_code_usage": "no_code_needed",
                "reward_type": "discount_line",
                "program_type": "promotion_program",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "active": True,
                "discount_apply_on": "specific_products",
                "discount_specific_product_ids": [(6, 0, [self.drawerBlack.id])],
            }
        )
        # Apply all the programs
        self.order.recompute_coupon_lines()
        # Check that Large Cabinet and Pedal Bin has discount after apply program
        self.assertEqual(
            self.large_cabinet_line.discount,
            0,
            "The discount for Large Cabinet should be empty",
        )
        self.assertEqual(
            self.drawer_black_line.discount,
            10,
            "The discount for Drawer Black should be 10%",
        )
        # Check amount total after apply coupon
        self.assertEqual(
            self.order.amount_total,
            2710.0,
            "The order total with programs should be 2710.00",
        )

    def test_program_reward_discount_line_cheapest_product(self):
        """
        Test program with reward type is `discount_line` for cheapest product
        """
        # change product line price unit
        self.large_cabinet_line.price_unit = 10
        # Now we want to apply a 10% discount for cheapest product
        self.env["coupon.program"].create(
            {
                "name": "10% reduction for cheapest product",
                "promo_code_usage": "no_code_needed",
                "reward_type": "discount_line",
                "program_type": "promotion_program",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "active": True,
                "discount_apply_on": "cheapest_product",
            }
        )
        # Apply all the programs
        self.order.recompute_coupon_lines()
        # Check that Large Cabinet and Pedal Bin has discount after apply program
        self.assertEqual(
            self.large_cabinet_line.discount,
            10,
            "The cheapest product is Large Cabinet and discount should be 10%",
        )
        # Check amount total after apply coupon
        self.assertEqual(
            self.order.amount_total,
            2463.0,
            "The order total with programs should be 2463.00",
        )

    def test_program_reward_discount_line_on_order(self):
        """
        Test program with reward type is `discount_line` for all lines from sale order
        """
        # Now we want to apply a 10% discount for current sale order
        self.env["coupon.program"].create(
            {
                "name": "10% reduction for current Sale Order",
                "promo_code_usage": "no_code_needed",
                "reward_type": "discount_line",
                "program_type": "promotion_program",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "active": True,
                "discount_apply_on": "on_order",
            }
        )
        # Apply all the programs
        self.order.recompute_coupon_lines()
        # Check that paid products with discount
        self.assertEqual(
            self.large_cabinet_line.discount,
            10,
            "The discount for Large Cabinet should be 10%",
        )
        self.assertEqual(
            self.pedal_bin_line.discount, 10, "The discount for Pedal Bin should be 10%"
        )
        # Check that other products hasn't discount
        self.assertEqual(
            self.conference_chair_line.discount,
            10,
            "The discount for Conference Chair should be 10%",
        )
        self.assertEqual(
            self.drawer_black_line.discount,
            10,
            "The discount for Drawer Black should be 10%",
        )
        # Check amount total after apply coupon
        self.assertEqual(
            self.order.amount_total,
            2475.0,
            "The order total with programs should be 2475.00",
        )

    def test_program_reward_discount_line_on_next_order(self):
        coupon_program = self.env["coupon.program"].create(
            {
                "name": "10% reduction for current Sale Order",
                "promo_code_usage": "code_needed",
                "promo_applicability": "on_next_order",
                "reward_type": "discount_line",
                "program_type": "promotion_program",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "active": True,
                "discount_apply_on": "on_order",
                "promo_code": "discount_10_percent",
            }
        )
        self.env["sale.coupon.apply.code"].with_context(active_id=self.order.id).create(
            {"coupon_code": "discount_10_percent"}
        ).process_coupon()
        self.assertEqual(
            len(coupon_program.coupon_ids.ids),
            1,
            "You should get a coupon for you next order that will offer a free product B",
        )
        self.order.action_confirm()
        # It should not error even if the SO does not have the requirements
        # (700$ and 1 product A), since these requirements where only used
        # to generate the coupon that we are now applying
        self.env["sale.coupon.apply.code"].with_context(active_id=self.order.id).create(
            {"coupon_code": self.order.generated_coupon_ids[0].code}
        ).process_coupon()
        self.assertEqual(len(self.order.order_line), 4)
        self.order.recompute_coupon_lines()
        self.assertEqual(len(self.order.order_line), 4)

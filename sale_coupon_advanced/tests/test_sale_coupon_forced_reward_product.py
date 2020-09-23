# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon


class TestSaleCouponForcedRewardProduct(TestSaleCouponCommon):
    def setUp(self):
        super().setUp()

        self.env["sale.coupon.program"].search([]).write({"active": False})

        # create partner for sale order.
        self.steve.lang = "en_US"

        self.order_forced = self.empty_order
        self.order_forced.write(
            {
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_A.id,
                            "name": "1 Product A",
                            "product_uom": self.uom_unit.id,
                            "product_uom_qty": 2.0,
                        },
                    )
                ]
            }
        )

        self.program_forced = self.env["sale.coupon.program"].create(
            {
                "name": "Buy anything, B are free",
                "promo_code_usage": "no_code_needed",
                "reward_type": "product",
                "reward_product_id": self.product_B.id,
                "rule_products_domain": "[('sale_ok', '=', True)]",
                "is_reward_product_forced": True,
                "active": True,
                "sequence": 1,
            }
        )
        self.reward_product = self.program_forced.reward_product_id
        self.discount_product = self.program_forced.discount_line_product_id

    def test_01_filter_programs_from_common_rules__result(self):
        """
            Testing `_filter_programs_from_common_rules`
        """
        # TODO adapt the test
        programs = self.program_forced._filter_programs_from_common_rules(
            self.order_forced
        )
        self.assertIn(
            self.program_forced.id,
            programs.ids,
            "`sale_coupon_program._filter_programs_from_common_rules` should "
            "return the program for the forced reward product",
        )

    def _test_02_get_reward_line_values__result(self):
        """
            Testing `sale_order._get_reward_line_values` strict formalism return

            IMPORTANT : be aware of the partner's lang as the discount product
            name is changed towards reward product name (addition of
            translatable `Free product - ` string)
        """
        taxes = [(4, tax.id, False) for tax in self.product_B.taxes_id]
        if self.order_forced.fiscal_position_id:
            taxes = self.order_forced.fiscal_position_id.map_tax(taxes)
        self.reward_values = [
            {
                "sequence": 998,
                "name": self.reward_product.name,
                "product_id": self.reward_product.id,
                "price_unit": self.reward_product.lst_price,
                "is_reward_line": False,
                "product_uom_qty": self.program_forced.reward_product_quantity,
                "product_uom": self.discount_product.uom_id.id,
                "tax_id": taxes,
            },
            {
                "sequence": 999,
                "name": self.discount_product.name,
                "product_id": self.discount_product.id,
                "price_unit": -self.reward_product.lst_price,
                "is_reward_line": True,
                "product_uom_qty": self.program_forced.reward_product_quantity,
                "product_uom": self.reward_product.uom_id.id,
                "tax_id": taxes,
            },
        ]

        # Sorting by sequences as the interface does
        reward_values = sorted(
            self.order_forced._get_reward_line_values(self.program_forced),
            key=lambda k: k["sequence"],
        )
        self.assertEquals(
            self.reward_values,
            reward_values,
            "`sale_order._get_reward_line_values` should return forced reward "
            "values",
        )

    def test_03_order_line__forced_reward_result(self):
        """
            Testing global result in sale_order.order_line :
                - all lines quantity must be 3
                - reward and discount respectively based on their product id
                - product discount should canceled the product reward price
        """
        self.order_forced.recompute_coupon_lines()
        all_lines = self.order_forced.order_line
        discount_lines = all_lines.filtered(
            lambda line: line.product_id.id == self.discount_product.id
        )
        discount_lines_by_price = discount_lines.filtered(
            lambda line: line.price_unit == -self.reward_product.lst_price
        )
        self.assertEqual(
            len(all_lines),
            3,
            "The order should contains the Product A line, the Product B "
            "reward line and the product B discount line",
        )
        self.assertTrue(
            self.order_forced._is_reward_in_order_lines(self.program_forced),
            "The order should contains the Product B reward line",
        )
        self.assertEquals(
            len(discount_lines),
            1,
            "The order should contains the Product B discount line",
        )
        self.assertEquals(
            len(discount_lines_by_price),
            1,
            "The order discount product should contains a negative reward price",
        )

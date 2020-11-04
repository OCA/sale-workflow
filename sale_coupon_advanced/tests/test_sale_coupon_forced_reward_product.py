# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form

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
                "name": "Promotion Buy anything, B is free",
                # Must specify program_type, because it does not set
                # it on default and just set False value.
                "program_type": "promotion_program",
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

    def _get_record_index(self, recordset, record):
        for i, rec in enumerate(recordset):
            if rec == record:
                return i
        raise ValueError("Record does not exist in recordset")

    def _test_auto_removed_discount(self, order, products, program):
        self.assertEqual(len(order.order_line), len(products))
        lines = order.order_line.filtered(lambda r: r.product_id in products)
        self.assertEqual(len(lines), len(products))
        self.assertNotIn(program, order.code_promo_program_id)
        self.assertNotIn(program, order.no_code_promo_program_ids)

    def _test_forced_reward_product_lines_pair(self, order, program):
        forced_line = order.order_line.filtered("forced_reward_line")
        self.assertEqual(len(forced_line), 1)
        self.assertEqual(forced_line.product_id, program.reward_product_id)
        reward_line = order.order_line.filtered("is_reward_line")
        self.assertEqual(len(reward_line), 1)
        self.assertEqual(reward_line.product_id, program.discount_line_product_id)

    def test_01_create_reward_line_forced(self):
        """Check if forced reward with counter lines are created."""
        self.order_forced._create_reward_line(self.program_forced)
        self.assertEqual(len(self.order_forced.order_line), 3)
        self._test_forced_reward_product_lines_pair(
            self.order_forced, self.program_forced
        )

    def test_02_order_line_forced_reward_result(self):
        """Check if forced product discount was applied.

        Case 1:
            - all lines quantity must be 3
            - reward and discount respectively based on their product id
            - product discount should canceled the product reward price
        Case 2: discount product unlinked, when reward product unlinked.
            Form case.
        Case 3: discount product unlinked, when reward product unlinked.
            backend case.
        Case 4: reward product not unlinked, when discount product is
            unlinked.
        """
        # Case 1.
        order = self.order_forced
        order.recompute_coupon_lines()
        all_lines = order.order_line
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
            order._is_reward_in_order_lines(self.program_forced),
            "The order should contains the Product B reward line",
        )
        self.assertEqual(
            len(discount_lines),
            1,
            "The order should contains the Product B discount line",
        )
        self.assertEqual(
            len(discount_lines_by_price),
            1,
            "The order discount product should contains a negative reward price",
        )
        # Case 2.
        reward_line = order.order_line.filtered(
            lambda r: r.product_id == self.reward_product
        )
        reward_line_idx = self._get_record_index(order.order_line, reward_line)
        # Use Form to mimic actual line remove via interface.
        with Form(order) as so:
            so.order_line.remove(reward_line_idx)
        self._test_auto_removed_discount(order, self.product_A, self.program_forced)
        # Case 3.
        order.recompute_coupon_lines()
        reward_line = order.order_line.filtered(
            lambda r: r.product_id == self.reward_product
        )
        reward_line.unlink()
        self._test_auto_removed_discount(order, self.product_A, self.program_forced)
        # Case 4.
        order.recompute_coupon_lines()
        # Sanity check.
        self.assertEqual(len(order.order_line), 3)
        discount_line = order.order_line.filtered(
            lambda r: r.product_id == self.discount_product
        )
        discount_line.unlink()
        self.assertEqual(len(order.order_line), 2)
        product_ids = order.order_line.mapped("product_id").ids
        self.assertEqual(
            sorted(product_ids), sorted((self.product_A | self.reward_product).ids)
        )

    def test_03_order_line_forced_reward_result(self):
        """Unlink promo product and try to use 6 code on discount."""
        order = self.order_forced
        order.recompute_coupon_lines()
        lines_code_6 = order.order_line.filtered(
            lambda r: r.product_id in (self.discount_product, self.product_A)
        )
        reward_line = order.order_line.filtered(
            lambda r: r.product_id == self.reward_product
        )
        order.write({"order_line": [(2, reward_line.id), (6, 0, lines_code_6.ids)]})
        self._test_auto_removed_discount(order, self.product_A, self.program_forced)

    def test_04_order_line_forced_reward_result(self):
        """Apply forced rewards with coupon code.

        Case 1: apply using code.
        Case 2: check if its not applied when recomputing promotions (
            promo inactive).
        Case 3: check if auto promotion applied, but not ones with code,
            when recomputing promotions (promo active).


        """
        self.program_forced.active = False
        # Case 1.
        program_product_1 = self.env["sale.coupon.program"].create(
            {
                "name": "Coupon buy anything, B is free",
                "program_type": "promotion_program",
                "promo_code_usage": "code_needed",
                "promo_code": "MYPROMO1",
                "reward_type": "product",
                "reward_product_id": self.product_B.id,
                "rule_products_domain": "[('sale_ok', '=', True)]",
                "is_reward_product_forced": True,
                "active": True,
                "sequence": 1,
            }
        )
        # Add extra promotion, to make sure it is not applied when not
        # needed.
        program_product_1.copy(
            default={
                "name": "Buy anything, C is free",
                "promo_code": "MYPROMO2",
                "reward_product_id": self.product_C.id,
            }
        )
        amount_total = self.order_forced.amount_total
        wizard = (
            self.env["sale.coupon.apply.code"]
            .with_context(active_id=self.order_forced.id)
            .create({"coupon_code": "MYPROMO1"})
        )
        wizard.process_coupon()
        # Existing line, plus free product with its discount line.
        self.assertEqual(len(self.order_forced.order_line), 3)
        # Total amount must not change, extra product is nullified by
        # discount line.
        self.assertEqual(self.order_forced.amount_total, amount_total)
        self._test_forced_reward_product_lines_pair(
            self.order_forced, program_product_1
        )
        # Case 2.
        self.order_forced.order_line.unlink()
        self.order_forced.recompute_coupon_lines()
        self.assertFalse(self.order_forced.order_line)
        # Case 3.
        self.order_forced.order_line = [
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
        self.program_forced.active = True
        self.order_forced.recompute_coupon_lines()
        self._test_forced_reward_product_lines_pair(
            self.order_forced, self.program_forced
        )

# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon


class TestSaleCoupon(TestSaleCouponCommon):
    def setUp(self):
        super().setUp()

        self.env["sale.coupon.program"].search([]).write({"active": False})

        self.product_D = self.env["product.product"].create(
            {
                "name": "Product D",
                "list_price": 100,
                "sale_ok": True,
                "taxes_id": [(6, 0, [])],
            }
        )

        self.program_a = self.env["sale.coupon.program"].create(
            {
                "name": "Program A",
                "promo_code_usage": "no_code_needed",
                "reward_type": "product",
                "reward_product_id": self.product_C.id,
                "rule_products_domain": "[('id', 'in', [%s])]" % (self.product_A.id),
                "active": True,
                "sequence": 1,
            }
        )
        self.program_b = self.env["sale.coupon.program"].create(
            {
                "name": "Program B",
                "promo_code_usage": "no_code_needed",
                "reward_type": "discount",
                "rule_products_domain": "[('id', 'in', [%s])]" % (self.product_A.id),
                "active": True,
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "sequence": 2,
            }
        )
        self.program_c = self.env["sale.coupon.program"].create(
            {
                "name": "Program C",
                "promo_code_usage": "no_code_needed",
                "reward_type": "product",
                "reward_product_id": self.product_D.id,
                "rule_products_domain": "[('id', 'in', [%s])]" % (self.product_A.id),
                "active": True,
                "sequence": 3,
            }
        )

    def _create_order(self):
        order = self.empty_order

        order.write(
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
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_B.id,
                            "name": "2 Product B",
                            "product_uom": self.uom_unit.id,
                            "product_uom_qty": 2.0,
                        },
                    ),
                    # product D and C will be minused for reward line
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_C.id,
                            "name": "1 Product C",
                            "product_uom": self.uom_unit.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_D.id,
                            "name": "1 Product D",
                            "product_uom": self.uom_unit.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                ]
            }
        )
        return order

    def test_all_programs_cumulative_auto_apply(self):
        # all programs applied
        order = self._create_order()
        programs = order._get_applicable_no_code_promo_program()
        expected_result = self.program_a + self.program_b + self.program_c
        self.assertEqual(programs, expected_result)

    def test_non_cumulative_programs_auto_apply(self):
        # programs is cutted to first cumulative
        self.program_b.is_cumulative = True
        order = self._create_order()
        programs = order._get_applicable_no_code_promo_program()
        expected_result = self.program_a + self.program_b
        self.assertEqual(programs, expected_result)

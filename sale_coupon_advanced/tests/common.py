# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon


# TODO: refactor to use SavepointCase. TransactionCase is bottlenecking
# tests here.
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

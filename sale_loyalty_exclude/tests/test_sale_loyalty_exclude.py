# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.sale_loyalty.tests.common import TestSaleCouponCommon


class TestSaleLoyaltyExclude(TestSaleCouponCommon):
    def _create_sale_order(self):
        order = self.env["sale.order"].create(
            {"partner_id": self.env["res.partner"].create({"name": "My Partner"}).id}
        )
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
                            "product_uom_qty": 10.0,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_B.id,
                            "name": "2 Product B",
                            "product_uom": self.uom_unit.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                ]
            }
        )
        return order

    def test_sale_loyalty_exclude(self):
        self.immediate_promotion_program.rule_ids.minimum_amount = 1000
        order = self._create_sale_order()
        self._auto_rewards(order, self.immediate_promotion_program)
        self.assertEqual(
            len(order.order_line.ids),
            3,
            "The promo offer should have been applied",
        )

        self.product_A.loyalty_exclude = True
        order = self._create_sale_order()
        self._auto_rewards(order, self.immediate_promotion_program)
        self.assertEqual(
            len(order.order_line.ids),
            2,
            "The promo offer shouldn't have been applied",
        )

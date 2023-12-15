# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.sale_loyalty.tests.common import TestSaleCouponCommon


class TestProgramRules(TestSaleCouponCommon):
    @classmethod
    def setUpClass(cls):
        super(TestProgramRules, cls).setUpClass()
        cls.industry_model = cls.env["res.partner.industry"]
        cls.industry_main = cls.industry_model.create({"name": "Main Industry"})
        cls.industry_A = cls.env.ref("base.res_partner_industry_A")
        cls.industry_A.parent_id = cls.industry_main
        cls.industry_B = cls.env.ref("base.res_partner_industry_B")
        cls.industry_B.parent_id = cls.industry_main

    def _create_sale_order(self):
        order = self.env["sale.order"].create({"partner_id": self.steve.id})
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

    def test_program_rules_no_industry(self):
        self.immediate_promotion_program.industry_ids = False

        order = self._create_sale_order()
        self._auto_rewards(order, self.immediate_promotion_program)
        self.assertEqual(
            len(order.order_line.ids),
            3,
            "The promo offer should have been applied as no industry is set.",
        )

    def test_program_applied_on_customer_industry(self):
        self.immediate_promotion_program.industry_ids = self.industry_A
        self.steve.industry_id = self.industry_B
        order = self._create_sale_order()
        self._auto_rewards(order, self.immediate_promotion_program)
        self.assertEqual(
            len(order.order_line.ids),
            2,
            "The promo offer is not applied to industry_B.",
        )
        self.immediate_promotion_program.industry_ids = self.industry_B
        order = self._create_sale_order()
        self._auto_rewards(order, self.immediate_promotion_program)
        self.assertEqual(
            len(order.order_line.ids),
            3,
            "The promo offer should have been applied as to industry_B",
        )

    def test_program_rules_with_customer_parent_industry(self):
        self.steve.industry_id = self.industry_main
        order = self._create_sale_order()
        self._auto_rewards(order, self.immediate_promotion_program)
        self.assertEqual(
            len(order.order_line.ids),
            3,
            "Promo offer applied as the main_industry is a parent industry_B",
        )

    def test_program_rules_with_customer_child_industry(self):
        self.steve.industry_id = self.industry_B
        self.immediate_promotion_program.industry_ids = self.industry_main
        order = self._create_sale_order()
        self._auto_rewards(order, self.immediate_promotion_program)
        self.assertEqual(
            len(order.order_line.ids),
            3,
            "Promo offer applied as industry_B is a child of main_industry",
        )

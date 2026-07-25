# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, new_test_user, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSaleOrderLineFinalPrice(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, test_sale_order_line_final_price=True)
        )
        # The expected figures below depend on these precisions
        cls.env.ref("product.decimal_price").digits = 2
        cls.env.ref("product.decimal_discount").digits = 2
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "consu",
                "list_price": 100.0,
                "taxes_id": False,
            }
        )
        # Nothing for a discount to move, so the final price is the unit one
        cls.product_free = cls.env["product.product"].create(
            {
                "name": "Test product free",
                "type": "consu",
                "list_price": 0.0,
                "taxes_id": False,
            }
        )
        cls.salesman = new_test_user(
            cls.env,
            login="price-lock-salesman",
            groups="sales_team.group_sale_salesman,sale.group_discount_per_so_line",
        )
        cls.manager = new_test_user(
            cls.env,
            login="price-lock-manager",
            groups="sales_team.group_sale_manager,sale.group_discount_per_so_line",
        )
        cls.order = (
            cls.env["sale.order"]
            .with_user(cls.manager)
            .create(
                {
                    "partner_id": cls.partner.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": cls.product.id,
                                "price_unit": 100,
                                "discount": 0,
                            }
                        )
                    ],
                }
            )
        )
        cls.line = cls.order.order_line

    def test_price_final(self):
        self.assertEqual(self.line.price_final, 100)
        # It keeps following any further change of its sources
        self.line.discount = 10
        self.assertEqual(self.line.price_final, 90)
        # Set final price under unit price
        self.line.price_final = 80
        self.assertEqual(self.line.price_unit, 100)
        self.assertEqual(self.line.discount, 20)
        # Set final price over unit price
        self.line.price_final = 120
        self.assertEqual(self.line.price_unit, 100)
        self.assertEqual(self.line.discount, -20)
        # Set final price with infinite decimals
        self.line.price_final = 33.33
        self.assertEqual(self.line.discount, 66.67)

    def test_price_final_without_unit_price(self):
        """The line is created with the agreed price as its unit price, and the
        amounts take it into account."""
        self.order.order_line = [
            Command.create({"product_id": self.product_free.id, "discount": 10})
        ]
        line = self.order.order_line[-1]
        line.price_final = 50
        self.assertEqual(line.price_unit, 50)
        self.assertEqual(line.discount, 0)

    def test_price_edit_allowed(self):
        self.assertFalse(self.line.with_user(self.salesman).price_edit_allowed)
        self.assertTrue(self.line.with_user(self.manager).price_edit_allowed)

    def test_prices_locked_for_salesman(self):
        with Form(self.env["sale.order"].with_user(self.salesman)) as order_form:
            order_form.partner_id = self.partner
            with order_form.order_line.new() as line_form:
                line_form.product_id = self.product
                with self.assertRaisesRegex(AssertionError, "readonly"):
                    line_form.price_unit = 60
                with self.assertRaisesRegex(AssertionError, "readonly"):
                    line_form.discount = 10

#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import Form, tagged

from odoo.addons.sale.tests.common import SaleCommon


@tagged("post_install", "-at_install")
class TestSalePrices(SaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Show the discounts in the sale order lines
        cls._enable_discounts()

    def _create_rule(self, **values):
        rule_values = {
            "pricelist_id": self.pricelist.id,
            "discount2": 20,
            "discount3": 30,
        }
        rule_values.update(values)
        return self.env["product.pricelist.item"].create(rule_values)

    def _add_order_line(self, order=None, product=None):
        order_form = Form(order or self.empty_order)
        with order_form.order_line.new() as line:
            line.product_id = product or self.product
        order = order_form.save()
        return order.order_line[-1]

    def test_percentage_discount_shown(self):
        """A percentage Discount Rule propagates the discounts
        to the sale order line when the discounts are shown.
        """
        # Arrange
        rule = self._create_rule(compute_price="percentage", percent_price=10)
        # pre-condition
        self.assertTrue(rule._show_discount())
        self.assertEqual(self.product.list_price, 20)

        # Act
        line = self._add_order_line()

        # Assert
        self.assertTrue(rule.price.startswith("49.6 % discount"))
        self.assertEqual(line.pricelist_item_id, rule)
        self.assertEqual(line.discount1, 10)
        self.assertEqual(line.discount2, 20)
        self.assertEqual(line.discount3, 30)
        self.assertAlmostEqual(line.discount, 49.6)
        self.assertEqual(line.price_unit, 20)
        self.assertEqual(line.price_subtotal, 10.08)
        # The patched discount of the rule has been restored
        self.assertEqual(rule.percent_price, 10)

    def test_percentage_discount_shown_create(self):
        """The discounts are propagated when the line is created without a form."""
        # Arrange
        self._create_rule(compute_price="percentage", percent_price=10)
        order = self.empty_order

        # Act
        order.order_line = [Command.create({"product_id": self.product.id})]

        # Assert
        line = order.order_line
        self.assertEqual(line.discount1, 10)
        self.assertEqual(line.discount2, 20)
        self.assertEqual(line.discount3, 30)
        self.assertEqual(line.price_unit, 20)
        self.assertEqual(line.price_subtotal, 10.08)

    def test_percentage_discount_hidden(self):
        """A percentage Discount Rule does not propagate the discounts
        to the sale order line when the discounts are hidden:
        they are included in the unit price.
        """
        # Arrange
        self.env.user.group_ids -= self.group_discount_per_so_line
        rule = self._create_rule(compute_price="percentage", percent_price=10)
        # pre-condition
        self.assertFalse(rule._show_discount())

        # Act
        line = self._add_order_line()

        # Assert
        self.assertTrue(rule.price.startswith("49.6 % discount"))
        self.assertFalse(line.discount1)
        self.assertFalse(line.discount2)
        self.assertFalse(line.discount3)
        self.assertEqual(line.price_unit, 10.08)
        self.assertEqual(line.price_subtotal, 10.08)

    def test_percentage_single_discount(self):
        """A rule without additional discounts behaves as in standard."""
        # Arrange
        rule = self._create_rule(
            compute_price="percentage",
            percent_price=10,
            discount2=0,
            discount3=0,
        )

        # Act
        line = self._add_order_line()

        # Assert
        self.assertTrue(rule.price.startswith("10 % discount"))
        self.assertEqual(line.discount1, 10)
        self.assertFalse(line.discount2)
        self.assertFalse(line.discount3)
        self.assertEqual(line.price_unit, 20)
        self.assertEqual(line.price_subtotal, 18)

    def test_percentage_on_other_pricelist(self):
        base_pricelist = self.env["product.pricelist"].create(
            {
                "name": "Base",
                "item_ids": [
                    Command.create({"compute_price": "percentage", "percent_price": 10})
                ],
            }
        )
        self._create_rule(
            compute_price="percentage",
            percent_price=20,
            base="pricelist",
            base_pricelist_id=base_pricelist.id,
            discount2=0,
            discount3=0,
        )
        line = self._add_order_line()
        self.assertAlmostEqual(line.discount, 28)
        self.assertEqual(line.price_subtotal, 14.4)

    def test_formula(self):
        """A formula Rule does not propagate the discounts to the sale order line:
        they are included in the unit price.
        """
        # Arrange
        rule = self._create_rule(compute_price="formula", price_discount=10)
        # pre-condition
        self.assertFalse(rule._show_discount())

        # Act
        line = self._add_order_line()

        # Assert
        self.assertTrue(rule.price.startswith("49.6 % discount"))
        self.assertIn("with a 49.6 % discount", rule.rule_tip)
        self.assertFalse(line.discount1)
        self.assertFalse(line.discount2)
        self.assertFalse(line.discount3)
        self.assertEqual(line.price_unit, 10.08)
        self.assertEqual(line.price_subtotal, 10.08)
        # The patched discount of the rule has been restored
        self.assertEqual(rule.price_discount, 10)

    def test_formula_markup(self):
        self.product.standard_price = 10
        rule = self._create_rule(
            compute_price="formula",
            base="standard_price",
            price_markup=20,
            discount2=10,
            discount3=0,
        )
        line = self._add_order_line()
        # 10 * 1.2 * 0.9 = 10.8, i.e. 8% markup
        self.assertTrue(rule.price.startswith("8 % markup"))
        self.assertEqual(line.price_unit, 10.8)
        self.assertEqual(rule.price_markup, 20)

    def test_change_product(self):
        """The discounts are reset when the rule no longer applies to the line."""
        # Arrange
        self._create_rule(
            compute_price="percentage",
            percent_price=10,
            applied_on="0_product_variant",
            product_id=self.product.id,
        )
        line = self._add_order_line()
        # pre-condition
        self.assertEqual(line.discount2, 20)
        self.assertEqual(line.discount3, 30)

        # Act
        line.product_id = self.service_product

        # Assert
        self.assertFalse(line.pricelist_item_id)
        self.assertFalse(line.discount1)
        self.assertFalse(line.discount2)
        self.assertFalse(line.discount3)
        self.assertFalse(line.discount)

    def test_recompute_prices(self):
        """Updating the prices of the order applies the discounts of the new rule."""
        # Arrange
        line = self._add_order_line()
        order = line.order_id
        # pre-condition
        self.assertFalse(line.discount1)
        self.assertFalse(line.discount2)
        self.assertFalse(line.discount3)

        # Act
        self._create_rule(compute_price="percentage", percent_price=10)
        order._recompute_prices()

        # Assert
        self.assertEqual(line.discount1, 10)
        self.assertEqual(line.discount2, 20)
        self.assertEqual(line.discount3, 30)
        self.assertAlmostEqual(line.discount, 49.6)
        self.assertEqual(line.price_unit, 20)
        self.assertEqual(line.price_subtotal, 10.08)

    def test_discount_restored_on_error(self):
        """The discount of the rule is restored
        when the computation of the price fails.
        """
        # Arrange
        rule = self._create_rule(compute_price="percentage", percent_price=10)
        product = self.product

        # Act
        with (
            mock.patch.object(
                type(rule),
                "_compute_base_price",
                side_effect=UserError("Test error"),
            ),
            self.assertRaises(UserError),
        ):
            rule._compute_price(product, 1, product.uom_id, self.empty_order.date_order)

        # Assert
        self.assertEqual(rule.percent_price, 10)

    def test_pricelist_readonly(self):
        """A user with readonly access on pricelists can read them and their items."""
        # Arrange
        self._create_rule(compute_price="percentage", percent_price=10)
        readonly_pricelist = self.pricelist.with_user(self.sale_user)
        # pre-condition
        self.assertTrue(readonly_pricelist.has_access("read"))
        self.assertFalse(readonly_pricelist.has_access("write"))

        # Assert
        readonly_pricelist.read()
        rule_values = readonly_pricelist.item_ids.read()[0]
        self.assertTrue(rule_values["price"].startswith("49.6 % discount"))

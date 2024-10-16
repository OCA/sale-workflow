#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import first
from odoo.tests import Form, tagged

from odoo.addons.sale.tests.common import SaleCommon


@tagged("post_install", "-at_install")
class TestSalePrices(SaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable user groups to be able to set advanced fields using Form
        pricelist_groups = [
            "product.group_discount_per_so_line",  # for product.pricelist.discount_policy
            "product.group_sale_pricelist",  # for product.pricelist.item.compute_price
        ]
        user = cls.env.user
        for pricelist_group in pricelist_groups:
            user.groups_id += cls.env.ref(pricelist_group)

    def test_percentage_with_discount(self):
        """A percentage Discount Rule in a "with_discount" Pricelist
        does not propagate the discounts to the sale order line.
        """
        # Arrange
        order = self.empty_order
        pricelist_form = Form(self.pricelist)
        pricelist_form.discount_policy = "with_discount"
        with pricelist_form.item_ids.new() as item:
            item.compute_price = "percentage"
            item.percent_price = 10
            item.discount2 = 20
            item.discount3 = 30
        pricelist = pricelist_form.save()
        rule = first(pricelist.item_ids)
        product = self.product
        # pre-condition
        self.assertEqual(pricelist.discount_policy, "with_discount")
        self.assertEqual(rule.compute_price, "percentage")
        self.assertEqual(rule.percent_price, 10)
        self.assertEqual(rule.discount2, 20)
        self.assertEqual(rule.discount3, 30)
        self.assertEqual(product.list_price, 20)

        # Act
        order_form = Form(order)
        with order_form.order_line.new() as line:
            line.product_id = product
        order = order_form.save()

        # Assert
        rule_explanation = "49.6 % discount"
        self.assertIn(rule_explanation, rule.price)
        line = order.order_line
        self.assertFalse(line.discount)
        self.assertFalse(line.discount2)
        self.assertFalse(line.discount3)
        self.assertEqual(line.price_unit, 10.08)
        self.assertEqual(line.price_subtotal, 10.08)

    def test_percentage_without_discount(self):
        """A percentage Discount Rule in a "without_discount" Pricelist
        propagates the discounts to the sale order line.
        """
        # Arrange
        order = self.empty_order
        pricelist_form = Form(self.pricelist)
        pricelist_form.discount_policy = "without_discount"
        with pricelist_form.item_ids.new() as item:
            item.compute_price = "percentage"
            item.percent_price = 10
            item.discount2 = 20
            item.discount3 = 30
        pricelist = pricelist_form.save()
        rule = first(pricelist.item_ids)
        product = self.product
        # pre-condition
        self.assertEqual(pricelist.discount_policy, "without_discount")
        self.assertEqual(rule.compute_price, "percentage")
        self.assertEqual(rule.percent_price, 10)
        self.assertEqual(rule.discount2, 20)
        self.assertEqual(rule.discount3, 30)
        self.assertEqual(product.list_price, 20)

        # Act
        order_form = Form(order)
        with order_form.order_line.new() as line:
            line.product_id = product
        order = order_form.save()

        # Assert
        rule_explanation = "49.6 % discount"
        self.assertIn(rule_explanation, rule.price)
        line = order.order_line
        self.assertEqual(line.discount, 10)
        self.assertEqual(line.discount2, 20)
        self.assertEqual(line.discount3, 30)
        self.assertEqual(line.price_unit, 20)
        self.assertEqual(line.price_subtotal, 10.08)

    def test_formula_with_discount(self):
        """A formula Discount Rule in a "with_discount" Pricelist
        does not propagate the discounts to the sale order line.
        """
        # Arrange
        order = self.empty_order
        pricelist_form = Form(self.pricelist)
        pricelist_form.discount_policy = "with_discount"
        with pricelist_form.item_ids.new() as item:
            item.compute_price = "formula"
            item.price_discount = 10
            item.discount2 = 20
            item.discount3 = 30
        pricelist = pricelist_form.save()
        rule = first(pricelist.item_ids)
        product = self.product
        # pre-condition
        self.assertEqual(pricelist.discount_policy, "with_discount")
        self.assertEqual(rule.compute_price, "formula")
        self.assertEqual(rule.price_discount, 10)
        self.assertEqual(rule.discount2, 20)
        self.assertEqual(rule.discount3, 30)
        self.assertEqual(product.list_price, 20)

        # Act
        order_form = Form(order)
        with order_form.order_line.new() as line:
            line.product_id = product
        order = order_form.save()

        # Assert
        rule_explanation = "49.6 % discount"
        self.assertIn(rule_explanation, rule.price)
        self.assertIn(rule_explanation, rule.rule_tip)
        line = order.order_line
        self.assertFalse(line.discount)
        self.assertFalse(line.discount2)
        self.assertFalse(line.discount3)
        self.assertEqual(line.price_unit, 10.08)
        self.assertEqual(line.price_subtotal, 10.08)

    def test_formula_without_discount(self):
        """A formula Discount Rule in a "without_discount" Pricelist
        propagates the discounts to the sale order line.
        """
        # Arrange
        order = self.empty_order
        pricelist_form = Form(self.pricelist)
        pricelist_form.discount_policy = "without_discount"
        with pricelist_form.item_ids.new() as item:
            item.compute_price = "formula"
            item.price_discount = 10
            item.discount2 = 20
            item.discount3 = 30
        pricelist = pricelist_form.save()
        rule = first(pricelist.item_ids)
        product = self.product
        # pre-condition
        self.assertEqual(pricelist.discount_policy, "without_discount")
        self.assertEqual(rule.compute_price, "formula")
        self.assertEqual(rule.price_discount, 10)
        self.assertEqual(rule.discount2, 20)
        self.assertEqual(rule.discount3, 30)
        self.assertEqual(product.list_price, 20)

        # Act
        order_form = Form(order)
        with order_form.order_line.new() as line:
            line.product_id = product
        order = order_form.save()

        # Assert
        rule_explanation = "49.6 % discount"
        self.assertIn(rule_explanation, rule.price)
        self.assertIn(rule_explanation, rule.rule_tip)
        line = order.order_line
        self.assertEqual(line.discount, 10)
        self.assertEqual(line.discount2, 20)
        self.assertEqual(line.discount3, 30)
        self.assertEqual(line.price_unit, 20)
        self.assertEqual(line.price_subtotal, 10.08)

    def test_pricelist_readonly(self):
        """A user with readonly access on pricelists can read them and their items."""
        # Arrange
        pricelist_form = Form(self.pricelist)
        pricelist_form.discount_policy = "with_discount"
        with pricelist_form.item_ids.new() as item:
            item.compute_price = "percentage"
            item.percent_price = 10
            item.discount2 = 20
            item.discount3 = 30
        pricelist = pricelist_form.save()
        readonly_pricelist = pricelist.with_user(self.sale_user)
        # pre-condition
        self.assertTrue(
            readonly_pricelist.check_access_rights("read", raise_exception=False)
        )
        self.assertFalse(
            readonly_pricelist.check_access_rights("write", raise_exception=False)
        )

        # Assert
        readonly_pricelist.read()
        readonly_pricelist.item_ids.read()

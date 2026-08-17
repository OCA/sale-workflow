# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPricelistCustomBasePrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100,
                "standard_price": 50,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Test Pricelist"})
        cls.pricelist_rule = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "0_product_variant",
                "product_id": cls.product.id,
                "compute_price": "formula",
                "base": "list_price",
            }
        )

    def test_pricelist_custom_base_price(self):
        # First, we will test the default behavior
        price = self.pricelist._get_product_price(self.product, 1)
        self.assertEqual(price, 100.0, "Default list price should be 100.0")

        # Now, we will test the custom base price
        self.pricelist_rule.write({"base": "custom_value"})
        price = self.pricelist._get_product_price(
            self.product,
            1,
            currency=self.pricelist.currency_id,
            custom_base_price=10,
        )
        self.assertEqual(price, 10.0, "Custom base price should be 10.0")

    def test_compute_base_price_with_currency_keyword(self):
        self.pricelist_rule.base = "custom_value"
        price = self.pricelist_rule.with_context(
            custom_base_price=10
        )._compute_base_price(
            self.product,
            1,
            self.product.uom_id,
            fields.Datetime.now(),
            currency=self.pricelist.currency_id,
        )
        self.assertEqual(price, 10.0)

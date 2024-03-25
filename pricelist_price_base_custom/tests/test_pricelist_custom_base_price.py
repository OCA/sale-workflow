# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
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
                "type": "product",
                "list_price": 100,
                "standard_price": 50,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Test Pricelist", "discount_policy": "without_discount"}
        )
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
        price = self.pricelist._get_product_price(self.product, 1, custom_base_price=10)
        self.assertEqual(price, 10.0, "Custom base price should be 10.0")

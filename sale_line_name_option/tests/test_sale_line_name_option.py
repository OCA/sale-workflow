# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleLineNameOption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "default_code": "TP001",
                "description_sale": "This is a test sale description.",
            }
        )

    def test_get_product_multiline_description_sale_excludes_code(self):
        result = self.product.get_product_multiline_description_sale()
        self.assertIn(self.product.default_code, result)
        self.env.company.no_product_code_in_sale_line_name = True
        result = self.product.get_product_multiline_description_sale()
        self.assertNotIn(self.product.default_code, result)
        self.assertIn(self.product.description_sale, result)

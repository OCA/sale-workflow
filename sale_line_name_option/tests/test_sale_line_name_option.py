# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleLineNameOption(BaseCommon):
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

    def test_prepare_invoice_line_no_duplicate_name(self):
        self.env.company.no_product_code_in_sale_line_name = True
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1},
                    )
                ],
            }
        )
        line = order.order_line
        self.assertNotIn(self.product.default_code, line.name)
        order.action_confirm()
        invoice_line_vals = line._prepare_invoice_line()
        self.assertEqual(invoice_line_vals["name"], line.name)

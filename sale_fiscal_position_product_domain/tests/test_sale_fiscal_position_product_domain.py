# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleFiscalPositionProductDomain(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax1 = cls.env["account.tax"].create({"name": "Tax 1", "amount": 10})
        cls.tax2 = cls.env["account.tax"].create({"name": "Tax 2", "amount": 20})
        cls.product = cls.env["product.product"].create(
            {"name": "AFP product", "taxes_id": [(4, cls.tax1.id)]}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "AFP product 2", "taxes_id": [(4, cls.tax1.id)]}
        )
        cls.customer = cls.env["res.partner"].create({"name": "AFP partner"})
        cls.fiscal_position = cls.env["account.fiscal.position"].create(
            {
                "name": "Test fiscal position",
                "product_domain": f"[('id', '=', {cls.product.product_tmpl_id.id})]",
                "tax_ids": [
                    (0, 0, {"tax_src_id": cls.tax1.id, "tax_dest_id": cls.tax2.id})
                ],
            }
        )
        cls.fiscal_position_ignored_domain = cls.env["account.fiscal.position"].create(
            {
                "name": "Test fiscal position ignored domain",
                "product_domain": f"[('id', '=', {cls.product.product_tmpl_id.id})]",
                "tax_ids": [
                    (
                        0,
                        0,
                        {
                            "tax_src_id": cls.tax1.id,
                            "tax_dest_id": cls.tax2.id,
                            "apply_product_domain": False,
                        },
                    )
                ],
            }
        )
        cls.fiscal_position_excluded_products = cls.env[
            "account.fiscal.position"
        ].create(
            {
                "name": "Test fiscal position excluded products",
                "product_domain": f"[('id', '=', {cls.product.product_tmpl_id.id})]",
                "tax_ids": [
                    (
                        0,
                        0,
                        {
                            "tax_src_id": cls.tax1.id,
                            "tax_dest_id": cls.tax2.id,
                            "apply_product_domain": "excluded",
                        },
                    )
                ],
            }
        )

    def _create_sale(self, fiscal_position):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.customer
        sale_form.fiscal_position_id = fiscal_position
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product2
        return sale_form.save()

    def test_fiscal_position_product_domain(self):
        sale = self._create_sale(self.fiscal_position)
        self.assertEqual(sale.order_line[0].tax_id, self.tax2)
        self.assertEqual(sale.order_line[1].tax_id, self.tax1)

    def test_fiscal_position_product_domain_ignored_on_line(self):
        sale = self._create_sale(self.fiscal_position_ignored_domain)
        self.assertEqual(sale.order_line[0].tax_id, self.tax2)
        self.assertEqual(sale.order_line[1].tax_id, self.tax2)

    def test_fiscal_position_product_domain_excluded_on_line(self):
        sale = self._create_sale(self.fiscal_position_excluded_products)
        self.assertEqual(sale.order_line[0].tax_id, self.tax1)
        self.assertEqual(sale.order_line[1].tax_id, self.tax2)

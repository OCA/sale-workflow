# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestSaleOrderCountryAllowedProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_test_1 = cls.env["product.template"].create(
            {
                "name": "Product-Test",
                "sale_allowed_country_ids": [
                    cls.env.ref("base.be").id,
                    cls.env.ref("base.fr").id,
                    cls.env.ref("base.es").id,
                ],
            }
        )
        cls.product_test_2 = cls.env["product.template"].create(
            {
                "name": "Product-Test",
                "sale_allowed_country_ids": [
                    cls.env.ref("base.us").id,
                ],
            }
        )
        cls.customer_test = cls.env["res.partner"].create(
            {"name": "Customer-Test", "country_id": cls.env.ref("base.us").id}
        )

    def test_product_availability(self):
        sale_form = Form(self.env["sale.order"], view="sale.view_order_form")
        sale_form.partner_id = self.customer_test
        context = {
            "restrict_by_country": True,
            "restrict_by_country_partner_id": sale_form.partner_shipping_id.id,
        }

        # Current user cannot get access to products unavailable in the shipping country
        available_products = (
            self.env["product.product"].with_context(**context)._search([])
        )
        self.assertFalse(
            self.product_test_1.product_variant_id.id in set(available_products)
        )
        self.assertTrue(
            self.product_test_2.product_variant_id.id in set(available_products)
        )

        so_line_form = sale_form.order_line.new()
        so_line_form.product_id = self.product_test_1.product_variant_id
        so_line_form.save()
        sale = sale_form.save()
        self.assertTrue(sale_form.unavailable_product_msg)
        with self.assertRaises(ValidationError):
            sale.action_confirm()

        # Current user is added to the group which gives access to all products
        self.env.user.write(
            {
                "groups_id": [
                    (
                        4,
                        self.env.ref(
                            "sale_order_country_allowed_product.ignore_country_sale"
                        ).id,
                    )
                ]
            }
        )
        available_products = (
            self.env["product.product"].with_context(**context)._search([])
        )
        self.assertTrue(
            self.product_test_1.product_variant_id.id in set(available_products)
        )
        self.assertTrue(
            self.product_test_2.product_variant_id.id in set(available_products)
        )
        sale.action_confirm()
        self.assertTrue(sale.state in ["sale", "done"])

# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserDemo


@tagged("post_install", "-at_install")
class TestSaleOrderTypeProductConfigurator(HttpCaseWithUserDemo):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company
        cls.sale_type_a = cls.env["sale.order.type"].create(
            {
                "name": "Type A",
                "company_id": cls.company.id,
            }
        )
        cls.sale_type_b = cls.env["sale.order.type"].create(
            {
                "name": "Type B",
                "company_id": cls.company.id,
            }
        )
        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "sale_ok": True,
                "sale_order_type_ids": [(6, 0, cls.sale_type_a.ids)],
            }
        )
        cls.attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Attribute",
                "create_variant": "always",
            }
        )
        cls.attribute_value_a = cls.env["product.attribute.value"].create(
            {
                "name": "Variant A",
                "attribute_id": cls.attribute.id,
            }
        )
        cls.attribute_value_b = cls.env["product.attribute.value"].create(
            {
                "name": "Variant B",
                "attribute_id": cls.attribute.id,
            }
        )
        cls.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": cls.product_tmpl.id,
                "attribute_id": cls.attribute.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            cls.attribute_value_a.id,
                            cls.attribute_value_b.id,
                        ],
                    )
                ],
            }
        )
        cls.variant_a = cls.product_tmpl.product_variant_ids.filtered(
            lambda product: (
                product.product_template_attribute_value_ids.name == "Variant A"
            )
        )
        cls.variant_b = cls.product_tmpl.product_variant_ids.filtered(
            lambda product: (
                product.product_template_attribute_value_ids.name == "Variant B"
            )
        )
        cls.variant_a.variant_sale_order_type_ids = cls.sale_type_a
        cls.variant_b.variant_sale_order_type_ids = cls.sale_type_b

    def _request_get_values(self, product_template, sale_order_type=None):
        base_url = product_template.get_base_url()
        response = self.opener.post(
            url=base_url + "/sale/product_configurator/get_values",
            json={
                "params": {
                    "product_template_id": product_template.id,
                    "quantity": 1.0,
                    "currency_id": self.company.currency_id.id,
                    "so_date": str(self.env.cr.now()),
                    "product_uom_id": None,
                    "company_id": None,
                    "pricelist_id": None,
                    "ptav_ids": None,
                    "only_main_product": False,
                    "sale_order_type_id": (
                        sale_order_type.id if sale_order_type else None
                    ),
                },
            },
        )
        return response.json()["result"]

    def test_product_configurator_filters_variants_by_sale_order_type(self):
        self.authenticate("demo", "demo")
        result = self._request_get_values(
            self.product_tmpl,
            self.sale_type_a,
        )
        archived_combinations = result["products"][0]["archived_combinations"]
        self.assertNotIn(
            self.variant_a.product_template_attribute_value_ids.ids,
            archived_combinations,
        )
        self.assertIn(
            self.variant_b.product_template_attribute_value_ids.ids,
            archived_combinations,
        )

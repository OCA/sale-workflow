# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from odoo.addons.base.tests.common import HttpCaseWithUserDemo
from odoo.addons.sale.tests.common import SaleCommon


class TestSalePackaging(HttpCaseWithUserDemo, SaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env["product.pricelist"].search([], limit=1)
        cls.currency = cls.env.company.currency_id
        prod_att_color = cls.env["product.attribute"].create({"name": "Color"})
        product_attr_val_red, product_attr_val_green = cls.env[
            "product.attribute.value"
        ].create(
            [
                {"name": "red", "attribute_id": prod_att_color.id, "sequence": 1},
                {"name": "blue", "attribute_id": prod_att_color.id, "sequence": 2},
            ]
        )
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Product 1",
            }
        )
        cls.product_template.attribute_line_ids = [
            (
                0,
                0,
                {
                    "attribute_id": prod_att_color.id,
                    "value_ids": [
                        (6, 0, [product_attr_val_red.id, product_attr_val_green.id])
                    ],
                },
            )
        ]

        cls.packaging_level = cls.env["product.packaging.level"].search(
            [("is_default", "=", True)]
        )
        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "Box 1",
                "product_id": cls.product_template.product_variant_ids[0].id,
                "packaging_level_id": cls.packaging_level.id,
            }
        )

    def setUp(self):
        super().setUp()
        self.authenticate(self.sale_manager.login, self.sale_manager.login)

    def test_sale_order_packaging(self):
        base_url = self.product_template.get_base_url()
        values = self.product_template.attribute_line_ids.product_template_value_ids
        response = self.opener.post(
            url=base_url + "/sale/product_configurator/get_values",
            json={
                "params": {
                    "product_template_id": self.product_template.id,
                    "quantity": 1.0,
                    "currency_id": 1,
                    "so_date": str(self.env.cr.now()),
                    "product_uom_id": None,
                    "company_id": None,
                    "pricelist_id": None,
                    "ptav_ids": values.ids,
                    "only_main_product": False,
                },
            },
        )
        result = json.loads(response.content)["result"]
        product = result["products"][0]
        self.assertEqual("Box 1", product["default_product_packaging_level_name"])

# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_attribute_model = cls.env["product.attribute"]
        cls.product_attribute_value_model = cls.env["product.attribute.value"]
        # Create product attributes
        cls.color_attribute = cls.product_attribute_model.create(
            {"name": "Color", "create_variant": "always"}
        )
        cls.color_values = cls.product_attribute_value_model.create(
            [
                {"name": "Red", "attribute_id": cls.color_attribute.id},
                {"name": "Blue", "attribute_id": cls.color_attribute.id},
                {"name": "Green", "attribute_id": cls.color_attribute.id},
            ]
        )
        cls.size_attribute = cls.product_attribute_model.create(
            {"name": "Size", "create_variant": "always"}
        )
        cls.size_values = cls.product_attribute_value_model.create(
            [
                {"name": "S", "attribute_id": cls.size_attribute.id},
                {"name": "M", "attribute_id": cls.size_attribute.id},
                {"name": "L", "attribute_id": cls.size_attribute.id},
            ]
        )

        # Create product template
        cls.product_template_1 = cls.env["product.template"].create(
            {
                "name": "Test Product 1",
            }
        )
        # Create product variants
        cls.product_template_2 = cls.env["product.template"].create(
            {
                "name": "Test Product 2",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.color_attribute.id,
                            "value_ids": [(6, 0, cls.color_values.ids)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.size_attribute.id,
                            "value_ids": [(6, 0, cls.size_values.ids)],
                        },
                    ),
                ],
            }
        )
        # Create secondary units
        cls.secondary_uom_1 = cls.env["product.secondary.unit"].create(
            {
                "name": "Unit 1",
                "uom_id": cls.product_uom_unit.id,
                "factor": 1,
                "product_tmpl_id": cls.product_template_1.id,
            }
        )
        cls.secondary_uom_2 = cls.env["product.secondary.unit"].create(
            {
                "name": "Unit 2",
                "uom_id": cls.product_uom_unit.id,
                "factor": 1,
                "product_tmpl_id": cls.product_template_1.id,
            }
        )
        cls.secondary_uom_3 = cls.env["product.secondary.unit"].create(
            {
                "name": "Unit 3",
                "uom_id": cls.product_uom_unit.id,
                "factor": 1,
                "product_tmpl_id": cls.product_template_2.id,
            }
        )
        cls.secondary_uom_4 = cls.env["product.secondary.unit"].create(
            {
                "name": "Unit 4",
                "uom_id": cls.product_uom_unit.id,
                "factor": 1,
                "product_tmpl_id": cls.product_template_2.id,
            }
        )

    def test_create_sets_sale_secondary_uom_id_for_single_variant(self):
        product_variant_ids = self.product_template_1.product_variant_ids
        product_variant_ids.sale_secondary_uom_id = self.secondary_uom_1
        self.assertEqual(self.product_template_1.sale_secondary_uom_id.name, "Unit 1")

    def test_create_not_sale_secondary_uom_id_for_variants_and_warns(self):
        product_variant_ids = self.product_template_2.product_variant_ids
        product_variant_ids[0].sale_secondary_uom_id = self.secondary_uom_3
        product_variant_ids[1].sale_secondary_uom_id = self.secondary_uom_4
        self.assertFalse(self.product_template_2.sale_secondary_uom_id)

        warning = self.product_template_2.onchange_sale_secondary_uom_id()
        self.assertIn("warning", warning)
        self.assertIn(
            "Product variants have distinct sale secondary uom",
            warning["warning"]["message"],
        )

    def test_create_sale_secondary_uom_id_multiple_variants_same_uom(self):
        product_variant_ids = self.product_template_2.product_variant_ids
        product_variant_ids[0].sale_secondary_uom_id = self.secondary_uom_3
        product_variant_ids[1].sale_secondary_uom_id = self.secondary_uom_3
        self.assertEqual(self.product_template_2.sale_secondary_uom_id.name, "Unit 3")

    def test_inverse_sale_secondary_uom_id_updates_variants_correctly(self):
        self.product_template_1.sale_secondary_uom_id = self.secondary_uom_2
        self.product_template_1._inverse_sale_secondary_uom_id()
        self.assertEqual(
            self.product_template_1.product_variant_ids.sale_secondary_uom_id,
            self.product_template_1.sale_secondary_uom_id,
        )

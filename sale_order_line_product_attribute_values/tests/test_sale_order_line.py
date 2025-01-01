# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class SomethingCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        # No create variant attributes
        cls.trademark_attribute = cls.env["product.attribute"].create(
            {
                "name": "Trademark",
                "display_type": "pills",
                "create_variant": "no_variant",
                "value_ids": [
                    Command.create({"name": "Adidas"}),
                    Command.create({"name": "Nike"}),
                    Command.create({"name": "Custom"}),
                ],
            }
        )
        cls.features_attribute = cls.env["product.attribute"].create(
            {
                "name": "Features",
                "display_type": "pills",
                "create_variant": "no_variant",
                "value_ids": [
                    Command.create({"name": "Windproof"}),
                    Command.create({"name": "Waterproof"}),
                ],
            }
        )
        cls.customization_attribute = cls.env["product.attribute"].create(
            {
                "name": "Customization",
                "display_type": "pills",
                "create_variant": "no_variant",
                "value_ids": [
                    Command.create({"name": "Front", "is_custom": True}),
                    Command.create({"name": "Rear", "is_custom": True}),
                ],
            }
        )
        # Create variant attributes
        cls.outer_material_attribute = cls.env["product.attribute"].create(
            {
                "name": "Outer Material",
                "display_type": "pills",
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "Corduroy"}),
                    Command.create({"name": "Polyester"}),
                    Command.create({"name": "Cotton"}),
                ],
            }
        )
        cls.inner_material_attribute = cls.env["product.attribute"].create(
            {
                "name": "Inner Material",
                "display_type": "pills",
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "Sheepskin fabric"}),
                    Command.create({"name": "Breathable fabric"}),
                ],
            }
        )
        cls.adidas, cls.nike, cls.custom = cls.trademark_attribute.value_ids
        cls.windproof, cls.waterproof = cls.features_attribute.value_ids
        cls.front, cls.rear = cls.customization_attribute.value_ids
        cls.corduroy, cls.polyester, cls.cotton = cls.outer_material_attribute.value_ids
        (
            cls.sheepskin_fabric,
            cls.breathable_fabric,
        ) = cls.inner_material_attribute.value_ids

        cls.custom_hoodie = cls.env["product.template"].create(
            {
                "name": "Custom Hoodie",
                "type": "service",
                "sale_ok": True,
            }
        )
        cls.env["product.template.attribute.line"].create(
            [
                {
                    "product_tmpl_id": cls.custom_hoodie.id,
                    "attribute_id": cls.trademark_attribute.id,
                    "value_ids": [Command.set([cls.custom.id])],
                },
                {
                    "product_tmpl_id": cls.custom_hoodie.id,
                    "attribute_id": cls.features_attribute.id,
                    "value_ids": [Command.set(cls.features_attribute.value_ids.ids)],
                },
                {
                    "product_tmpl_id": cls.custom_hoodie.id,
                    "attribute_id": cls.customization_attribute.id,
                    "value_ids": [
                        Command.set(cls.customization_attribute.value_ids.ids)
                    ],
                },
                {
                    "product_tmpl_id": cls.custom_hoodie.id,
                    "attribute_id": cls.outer_material_attribute.id,
                    "value_ids": [
                        Command.set(cls.outer_material_attribute.value_ids.ids)
                    ],
                },
                {
                    "product_tmpl_id": cls.custom_hoodie.id,
                    "attribute_id": cls.inner_material_attribute.id,
                    "value_ids": [
                        Command.set(cls.inner_material_attribute.value_ids.ids)
                    ],
                },
            ]
        )

    def test_line_has_all_attributes(self):
        """Test sale line has all selected attributes and inherited ones"""
        t_custom = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", self.custom_hoodie.id),
                ("attribute_id", "=", self.trademark_attribute.id),
                ("product_attribute_value_id", "=", self.custom.id),
            ]
        )
        f_windproof = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", self.custom_hoodie.id),
                ("attribute_id", "=", self.features_attribute.id),
                ("product_attribute_value_id", "=", self.windproof.id),
            ]
        )
        c_front = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", self.custom_hoodie.id),
                ("attribute_id", "=", self.customization_attribute.id),
                ("product_attribute_value_id", "=", self.front.id),
            ]
        )

        # Simulate real order creation
        custom_hoodie_variant = self.custom_hoodie.product_variant_ids[0]
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_template_id": self.custom_hoodie.id,
                            "product_id": custom_hoodie_variant.id,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )
        so.order_line.write(
            {
                "product_custom_attribute_value_ids": [
                    Command.create(
                        {
                            "custom_product_template_attribute_value_id": c_front.id,
                            "custom_value": "Odoo 16",
                        }
                    )
                ],
                "product_no_variant_attribute_value_ids": [
                    Command.set(
                        [
                            t_custom.id,
                            f_windproof.id,
                            c_front.id,
                        ]
                    )
                ],
            }
        )
        so.order_line._compute_custom_attribute_values()
        so.order_line._compute_no_variant_attribute_values()
        self.assertEqual(len(so.order_line.all_product_template_attribute_value_ids), 5)
        self.assertRecordValues(
            so.order_line,
            [
                {
                    "all_product_attribute_value_ids": [
                        self.custom.id,
                        self.windproof.id,
                        self.front.id,
                    ]
                    + custom_hoodie_variant.product_template_variant_value_ids.mapped(
                        "product_attribute_value_id"
                    ).ids,
                }
            ],
        )

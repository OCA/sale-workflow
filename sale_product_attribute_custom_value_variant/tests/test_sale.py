# Copyright 2025 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.product_attribute_custom_value_variant.tests.common import (
    AttributeValueVariantCommon,
)


class TestSale(AttributeValueVariantCommon):
    def test_sale(self):
        """When a product template is sold with a "Create custom variant"
        attribute value, a new attribute value is created and assigned to
         the new sold variant."""
        customer = self.customer
        product_template = self.glass_product_template
        attribute = self.length_attribute
        attribute_values = attribute.value_ids
        attribute_value = attribute_values.filtered("create_custom_variant")
        template_value = (
            product_template.attribute_line_ids.product_template_value_ids.filtered(
                lambda ptav: ptav.product_attribute_value_id == attribute_value
            )
        )
        product_variants = product_template.product_variant_ids
        custom_product_variant = product_variants.filtered(
            lambda variant: template_value
            in variant.product_template_attribute_value_ids
        )
        # pre-condition
        self.assertTrue(template_value.product_attribute_value_id.create_custom_variant)

        # Act
        custom_values_commands = [
            Command.create(
                {
                    "custom_product_template_attribute_value_id": template_value.id,
                    "custom_value": "15",
                }
            ),
        ]
        line_values = {
            "name": "Test line",
            "product_id": custom_product_variant.id,
            "product_custom_attribute_value_ids": custom_values_commands,
        }
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "order_line": [Command.create(line_values)],
            }
        )

        # Assert
        sold_variant = sale_order.order_line.product_id
        self.assertNotIn(sold_variant, product_variants)
        self.assertIn(sold_variant, product_template.product_variant_ids)

        new_attribute_value = attribute.value_ids - attribute_values
        sold_variant_attribute_values = (
            sold_variant.product_template_attribute_value_ids.product_attribute_value_id
        )
        self.assertIn(new_attribute_value, sold_variant_attribute_values)
        self.assertNotIn(attribute_value, sold_variant_attribute_values)
        self.assertNotIn(new_attribute_value, sold_variant.attribute_line_ids.value_ids)

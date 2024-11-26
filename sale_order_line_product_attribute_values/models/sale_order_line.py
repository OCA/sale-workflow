# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    all_product_template_attribute_value_ids = fields.Many2many(
        string="Product Template Attribute Values",
        comodel_name="product.template.attribute.value",
        relation="sale_order_line_all_product_template_attribute_value_rel",
        compute="_compute_all_product_template_attribute_value_ids",
        help="All Product Template Attribute Values used directly or indirecly "
        "for this line.",
        store=True,
        readonly=True,
    )
    all_product_attribute_value_ids = fields.Many2many(
        string="Attribute Values",
        comodel_name="product.attribute.value",
        relation="sale_order_line_all_product_attribute_value_rel",
        compute="_compute_all_product_template_attribute_value_ids",
        help="All Product Attribute Values used directly or indirecly "
        "for this line.\n"
        "Contains information about increased price, html color, etc.",
        store=True,
        readonly=True,
    )

    @api.depends(
        "product_id",
        "product_custom_attribute_value_ids",
        "product_no_variant_attribute_value_ids",
    )
    def _compute_all_product_template_attribute_value_ids(self):
        """Compute all Product Template Attribute Values used directly or indirecly"""
        if self.env.context.get("module") == "sale_order_line_product_attribute_values":
            # Do not trigger computation when module is installed alone
            # due to the large amount of records to compute
            return
        for record in self:
            product = record.product_id
            # Attribute values from the line
            pt_attr_values = record.product_no_variant_attribute_value_ids
            # Attribute values from the custom attributes
            pt_attr_values |= record.product_custom_attribute_value_ids.mapped(
                "custom_product_template_attribute_value_id"
            )
            # Attribute values from the product
            pt_attr_values |= product.product_template_variant_value_ids
            # Attribute values that doesn't need to be chosen from the product
            # because the variant is created with its values
            pt_attr_values |= product.product_template_attribute_value_ids
            # Attribute values from the product that doesn't need to be chosen
            # because doesn't create variant and has only one option
            for attr_l in product.valid_product_template_attribute_line_ids:
                if (
                    len(attr_l.value_ids) == 1
                    and attr_l.attribute_id.create_variant == "no_variant"
                ):
                    pt_attr_values |= attr_l.product_template_value_ids.filtered(
                        lambda ptav: ptav.ptav_active
                        and ptav.product_attribute_value_id in attr_l.value_ids
                    )
            record.all_product_template_attribute_value_ids = pt_attr_values
            record.all_product_attribute_value_ids = pt_attr_values.mapped(
                "product_attribute_value_id"
            )

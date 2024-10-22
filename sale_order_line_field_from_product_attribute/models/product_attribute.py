# Copyright (C) 2023 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    store_in_field = fields.Many2one(
        "ir.model.fields",
        domain="[('model', '=', 'sale.order.line')]",
        help="When selected, the attribute value will be stored in this field.",
    )


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    store_in_field_value = fields.Char(
        help="When storing in a value, use this value instead of the Attribute Value",
    )

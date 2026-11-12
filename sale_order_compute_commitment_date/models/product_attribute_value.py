# Copyright 2025 APSL Nagarro
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    lead_time = fields.Integer(
        help="The number of days this attribute adds to the product's lead time.",
    )

# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplateIdcategory(models.Model):
    _name = "product.template.id_category"
    _description = "Product Template Identification Category"

    product_tmpl_id = fields.Many2one("product.template")
    category_id = fields.Many2one("res.partner.id_category")
    is_mandatory = fields.Boolean(
        default=True, help="Defines whether identification is mandatory."
    )
    message = fields.Text(
        help="Allows you to define a description of why "
        "this identification is being added.\n"
        "Example: Asking the customer for identification"
    )

# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_allowed_country_ids = fields.Many2many(
        comodel_name="res.country", string="Sale Allowed Countries"
    )

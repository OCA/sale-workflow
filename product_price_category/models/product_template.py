# Copyright 2016 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    price_category_id = fields.Many2one(
        "product.price.category", string="Price Category", ondelete="restrict"
    )

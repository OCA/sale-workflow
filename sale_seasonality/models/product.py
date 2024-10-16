# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    next_campaign_ids = fields.Many2many(comodel_name="utm.campaign", help="Define which campaigns concern this product")

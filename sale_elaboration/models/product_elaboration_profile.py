# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductElaborationProfile(models.Model):
    _name = "product.elaboration.profile"
    _description = "Product elaboration profiles"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(string="Short Code")
    active = fields.Boolean(default=True)
    elaboration_ids = fields.Many2many(
        string="Elaborations",
        comodel_name="product.elaboration",
        relation="product_elaboration_profile_rel",
        column1="profile_id",
        column2="elaboration_id",
    )

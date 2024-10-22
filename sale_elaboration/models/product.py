# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    elaboration_profile_id = fields.Many2one(
        comodel_name="product.elaboration.profile", ondelete="restrict"
    )

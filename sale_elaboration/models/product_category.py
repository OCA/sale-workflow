# Copyright 2025 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    elaboration_profile_id = fields.Many2one(
        comodel_name="product.elaboration.profile", string="Elaboration Profile"
    )

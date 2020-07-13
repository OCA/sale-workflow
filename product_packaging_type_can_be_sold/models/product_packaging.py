# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    can_be_sold = fields.Boolean(
        related="packaging_type_id.can_be_sold", readonly=True,
    )

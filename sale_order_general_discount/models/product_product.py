# Copyright 2021 - Pierre Verkest
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    bypass_general_discount = fields.Boolean(
        string="Don't apply general discount",
        help="If this checkbox is not ticked, it means changing general discount on "
        "sale order will impact sale order lines with this related product.",
    )

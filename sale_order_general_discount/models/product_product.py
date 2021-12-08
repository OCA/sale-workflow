# Copyright 2021 - Pierre Verkest
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    general_discount_apply = fields.Boolean(
        string="Apply general discount",
        default=True,
        required=True,
        help="If this checkbox is ticked, it means changing general discount on sale order "
        "will impact sale order lines with this related product.",
    )

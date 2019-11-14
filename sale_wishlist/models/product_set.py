# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductSet(models.Model):

    _inherit = 'product.set'

    typology = fields.Selection(
        selection=[
            ("set", "Default"),
            ("wishlist", "Wishlist"),
        ],
        default="set",
    )

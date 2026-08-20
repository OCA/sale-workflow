# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    show_surcharge = fields.Boolean(
        default=False,
        help="If enabled, when the price is computed "
        "will show the customer the surcharge.",
    )

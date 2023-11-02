# Copyright 2019 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.addons.decimal_precision as dp
from openerp import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    discount2 = fields.Float(
        "Discount 2 (%)",
        digits_compute=dp.get_precision("Discount"),
        help="Second discount applied on a sale order line.",
        default=0.0,
    )

    discount3 = fields.Float(
        "Discount 3 (%)",
        digits_compute=dp.get_precision("Discount"),
        help="Third discount applied on a sale order line.",
        default=0.0,
    )

#  Copyright (c) 2019 Simone Rubino - Agile Business Group
#  Copyright (c) 2021 Andrea Cometa - Apulia Software s.r.l.
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
import odoo.addons.decimal_precision as dp


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    """
    total_discount = fields.Float(
        'Total Discount',
        digits=dp.get_precision('Discount'),
        default=0.0,
        compute='_compute_discount'
    )
    """

    discount2 = fields.Float(
        'Discount 2 (%)',
        digits=dp.get_precision('Discount'),
        help="Second discount applied on a sale order line.",
        default=0.0
    )

    discount3 = fields.Float(
        'Discount 3 (%)',
        digits=dp.get_precision('Discount'),
        help="Third discount applied on a sale order line.",
        default=0.0
    )

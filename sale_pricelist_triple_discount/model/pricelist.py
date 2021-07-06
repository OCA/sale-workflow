#  Copyright (c) 2019 Simone Rubino - Agile Business Group
#  Copyright (c) 2021 Andrea Cometa - Apulia Software s.r.l.
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
import odoo.addons.decimal_precision as dp


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

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

    def _compute_price(self, price, price_uom, product, quantity=1.0,
                       partner=False):
        """Compute the unit price of a product in the context of a pricelist
           application. The unused parameters are there to make the full
           context available for overrides.
        """
        price = super(ProductPricelistItem, self)._compute_price(
            price, price_uom, product, quantity, partner)

        self.ensure_one()
        if self.pricelist_id.discount_policy == 'with_discount' and \
                self.compute_price == 'formula':
            price = (price - (price * (self.discount2 / 100))) or 0.0
            price = (price - (price * (self.discount3 / 100))) or 0.0
        return price

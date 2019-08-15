# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False,
                      company=False):
        packs, no_packs = self.split_pack_products()
        prices = super(ProductProduct, no_packs).price_compute(
            price_type, uom, currency, company)
        for product in packs.with_context(prefetch_fields=False):
            pack_price = 0.0
            for pack_line in product.pack_line_ids:
                product_line_price = pack_line.product_id.price * (
                    1 - (pack_line.sale_discount or 0.0) / 100.0)
                pack_price += (product_line_price * pack_line.quantity)
            prices[product.id] = pack_price
        return prices

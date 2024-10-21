# Copyright 2019 Simone Rubino - Agile Business Group
# Copyright (c) 2021 Andrea Cometa - Apulia Software s.r.l.
# Copyright 2022 Alberto Re - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    discount2 = fields.Float(
        "Discount 2 (%)",
        digits="Discount",
        help="Second discount applied on a sale order line.",
        default=0.0,
    )

    discount3 = fields.Float(
        "Discount 3 (%)",
        digits="Discount",
        help="Third discount applied on a sale order line.",
        default=0.0,
    )

    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        """Compute the unit price of a product in the context of a pricelist
        application. The unused parameters are there to make the full
        context available for overrides.
        """
        self.ensure_one()

        if self.compute_price != "formula":
            return super()._compute_price(price, price_uom, product, quantity, partner)
        else:
            # Here we save price_round, then we temporarily unset it
            # to ensure super() calculates the price without applying
            # any rounding. We will apply the price_round only to the
            # subtotal after all discounts have been applied.
            store_price_round = self.price_round
            self.price_round = None
            price = super()._compute_price(price, price_uom, product, quantity, partner)
            self.price_round = store_price_round

            if self.pricelist_id.discount_policy == "with_discount":
                price = (price - (price * (self.discount2 / 100))) or 0.0
                price = (price - (price * (self.discount3 / 100))) or 0.0

            return price

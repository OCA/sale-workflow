# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, tools


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(
        selection_add=[("custom_value", "Custom Value")],
        ondelete={"custom_value": "set default"},
    )

    def _compute_price(self, product, quantity, uom, date, currency=None):
        if (
            "custom_base_price" in self.env.context
            and self.compute_price == "formula"
            and self.base == "custom_value"
        ):
            product_uom = product.uom_id
            if product_uom != uom:
                convert = lambda p: product_uom._compute_price(p, uom)  # noqa: E731
            else:
                convert = lambda p: p  # noqa: E731
            base_price = self.env.context.get("custom_base_price")
            price_limit = base_price
            price = (base_price - (base_price * (self.price_discount / 100))) or 0.0
            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)

            if self.price_surcharge:
                price += convert(self.price_surcharge)

            if self.price_min_margin:
                price = max(price, price_limit + convert(self.price_min_margin))

            if self.price_max_margin:
                price = min(price, price_limit + convert(self.price_max_margin))

            return price
        else:
            return super()._compute_price(product, quantity, uom, date, currency)

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def price_compute(
        self, price_type, uom=None, currency=None, company=None, date=False
    ):
        price_config = self.env.context.get("price_config")
        input_line = self.env.context.get("input_line")

        prices = dict.fromkeys(self.ids, 0.0)

        if price_config and input_line:
            for product in self:
                prices[product.id] = price_config._get_price(input_line)
            return prices

        return super().price_compute(price_type, uom, currency, company, date)

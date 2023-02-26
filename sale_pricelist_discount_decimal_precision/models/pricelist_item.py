from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    percent_price = fields.Float("Percentage Price", digits="Discount")
    price_discount = fields.Float("Price Discount", digits="Discount")

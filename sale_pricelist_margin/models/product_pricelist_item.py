from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    discount_type = fields.Selection(
        [("discount", "Discount"), ("sale_margin", "Sale Margin")],
        default="discount",
    )
    price_discount = fields.Float(
        readonly=False,
        compute="_compute_price_discount",
    )
    sale_margin = fields.Float(
        help="The margin percentage for sale price.",
    )

    @api.depends("sale_margin")
    def _compute_price_discount(self):
        for record in self:
            record.price_discount = (
                -1 * ((1 / (1 - (record.sale_margin / 100))) - 1) * 100
            )

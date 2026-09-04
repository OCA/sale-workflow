from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Legacy rounding in screen behavior
    price_unit = fields.Float(digits="Product Price")

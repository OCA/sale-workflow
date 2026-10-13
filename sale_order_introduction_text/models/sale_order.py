from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_introduction_text = fields.Html(
        help="This text will be displayed at the top of the sale order report.",
        default=lambda self: self.env.company.sale_order_introduction_text,
        translate=True,
    )

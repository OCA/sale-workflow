from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_order_introduction_text = fields.Html(
        help="This text will be displayed at the top of the sale order report.",
        translate=True,
    )

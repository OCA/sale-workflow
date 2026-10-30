from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_order_introduction_text = fields.Html(
        string="Sale Order Introduction Text",
        help="This text will be displayed at the top of the sale order report.",
        related="company_id.sale_order_introduction_text",
        readonly=False,
    )

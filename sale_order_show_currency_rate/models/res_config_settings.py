from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_order_currency_report_id = fields.Many2one(
        related="company_id.sale_order_currency_report_id",
        readonly=False,
    )

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    report_total_without_discount = fields.Boolean(
        related="company_id.report_total_without_discount", readonly=False
    )

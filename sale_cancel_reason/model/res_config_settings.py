from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_sale_cancel_reason = fields.Boolean(
        related="company_id.enable_sale_cancel_reason",
        readonly=False,
    )

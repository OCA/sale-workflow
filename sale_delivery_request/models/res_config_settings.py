from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    delivery_request_expiration_days = fields.Integer(
        related="company_id.delivery_request_expiration_days",
        readonly=False,
    )

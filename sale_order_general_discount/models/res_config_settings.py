from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    general_discount_applicable_to = fields.Text(
        related="company_id.general_discount_applicable_to", readonly=False
    )

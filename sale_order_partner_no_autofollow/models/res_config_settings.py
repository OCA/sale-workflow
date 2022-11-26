from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    partner_disable_autofollow = fields.Boolean(
        config_parameter="sale_order_partner_no_autofollow.disable_partner_autofollow",
        string="Customer disable autofollow",
    )

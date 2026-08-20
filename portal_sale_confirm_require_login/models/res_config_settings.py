from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    portal_sale_access_login_required = fields.Boolean(
        string="Require Login To Access Portal Sale Documents",
        config_parameter=(
            "portal_sale_confirm_require_login.portal_sale_access_login_required"
        ),
    )

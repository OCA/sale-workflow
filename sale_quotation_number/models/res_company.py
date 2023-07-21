from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    keep_name_so = fields.Boolean(
        "Use Same Enumeration",
        help="If this is unchecked, quotations use a different sequence from sale orders",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    keep_name_so = fields.Boolean(related="company_id.keep_name_so", readonly=False)

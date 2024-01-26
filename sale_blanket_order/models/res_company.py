from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    enable_numbered_bo = fields.Boolean("Enable numbered BO", default=False)

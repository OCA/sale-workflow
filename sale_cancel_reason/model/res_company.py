from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    enable_sale_cancel_reason = fields.Boolean(default=False)

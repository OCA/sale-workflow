from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    minimum_so_amount = fields.Float(string="Minimum Sale Amount")

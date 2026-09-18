from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    display_discount_with_tax = fields.Boolean(string="Show the Discount with TAX")
    report_total_without_discount = fields.Boolean()

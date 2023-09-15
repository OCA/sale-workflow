from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    report_total_without_discount = fields.Boolean("Report Total Without Discount")

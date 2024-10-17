from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    display_discount_with_tax = fields.Boolean(
        string="Show the Discount with TAX",
        help="Check this field to show the Discount with TAX",
        related="company_id.display_discount_with_tax",
        readonly=False,
    )
    report_total_without_discount = fields.Boolean(
        string="Report Total Without Discount",
        help='Display "Total without discount" in report',
        related="company_id.report_total_without_discount",
        readonly=False,
    )

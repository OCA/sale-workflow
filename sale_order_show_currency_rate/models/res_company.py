from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_order_currency_report_id = fields.Many2one(
        comodel_name="res.currency",
        string="Sale Order Report Reference Currency",
        help="Currency shown as informative exchange rate on sale order PDF reports "
        "when the order currency matches the company currency.",
    )

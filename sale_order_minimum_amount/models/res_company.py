from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_min_order_limit = fields.Float(
        string="Minimum Sales Order Amount",
        help=(
            "Sales users cannot confirm orders below this amount. "
            "Sales Managers are not restricted."
        ),
    )

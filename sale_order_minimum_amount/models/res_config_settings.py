from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_min_order_limit = fields.Float(
        string="Minimum Sales Order Amount",
        related="company_id.sale_min_order_limit",
        readonly=False,
        help=(
            "Sales users cannot confirm orders below this amount. "
            "Sales Managers are not restricted."
        ),
    )

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    display_line_weight_on_sale_report = fields.Boolean(
        related="company_id.display_line_weight_on_sale_report", readonly=False
    )
    display_order_weight_on_sale_report = fields.Boolean(
        related="company_id.display_order_weight_on_sale_report", readonly=False
    )

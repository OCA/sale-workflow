# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    no_product_code_in_sale_line_name = fields.Boolean(
        related="company_id.no_product_code_in_sale_line_name",
        readonly=False,
    )

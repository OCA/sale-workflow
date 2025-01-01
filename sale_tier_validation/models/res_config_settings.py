# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_report_print_block = fields.Boolean(
        related="company_id.sale_report_print_block",
        readonly=False,
        help="Block the printing of the sale order report if the order is not validated.",
    )

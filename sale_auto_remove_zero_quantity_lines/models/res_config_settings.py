# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_auto_remove_zero_quantity_lines = fields.Boolean(
        string="Automatic Removal of Zero Quantity Lines",
        related="company_id.sale_auto_remove_zero_quantity_lines",
        readonly=False,
        help="Auto remove sale order lines with zero quantity upon confirmation.",
    )

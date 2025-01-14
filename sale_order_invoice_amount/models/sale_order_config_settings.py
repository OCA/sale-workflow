# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_amount_invoiced_based_on_quantity = fields.Boolean(
        related="company_id.enable_amount_invoiced_based_on_quantity",
        readonly=False,
    )

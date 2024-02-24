# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_sale_cancel_confirmed_invoice = fields.Boolean(
        related="company_id.enable_sale_cancel_confirmed_invoice",
        readonly=False,
    )

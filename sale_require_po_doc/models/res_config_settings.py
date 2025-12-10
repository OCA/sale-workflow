# Copyright (C) 2026 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    customer_need_po_default = fields.Boolean(
        related="company_id.customer_need_po_default", readonly=False
    )

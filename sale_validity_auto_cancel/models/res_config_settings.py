# Copyright 2023 ForgeFlow S.L.
# Copyright 2024 OERP Canada <https://www.oerp.ca>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_validity_auto_cancel_days = fields.Integer(
        related="company_id.sale_validity_auto_cancel_days",
        readonly=False,
    )

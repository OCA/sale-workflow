# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    create_call_off_from_so_if_possible = fields.Boolean(
        related="company_id.create_call_off_from_so_if_possible",
        readonly=False,
        string="Create Call-Off from SO if possible",
        help="If checked, when a sales order is confirmed and some lines refer to a "
        "blanket order, these lines will be automatically moved to a new call-off "
        "order.",
    )

# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_to_change_lot_on_confirmed_so = fields.Boolean(
        string="Allow to change lot on confirmed sale order",
        related="company_id.allow_to_change_lot_on_confirmed_so",
        readonly=False,
    )

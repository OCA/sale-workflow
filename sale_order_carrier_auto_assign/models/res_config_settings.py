# Copyright 2023 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    carrier_auto_assign_on_create = fields.Boolean(
        related="company_id.carrier_auto_assign_on_create",
        readonly=False,
    )

    carrier_auto_assign_on_confirm = fields.Boolean(
        related="company_id.carrier_auto_assign_on_confirm",
        readonly=False,
    )

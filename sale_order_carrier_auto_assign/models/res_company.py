# Copyright 2023 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    carrier_auto_assign_on_create = fields.Boolean(
        "Set default shipping method automatically"
    )
    carrier_auto_assign_on_confirm = fields.Boolean(
        "Ensure shipping method and cost line on confirmation"
    )

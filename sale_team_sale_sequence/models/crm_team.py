# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sale Order Sequence",
        domain="[('company_id', 'in', [False, company_id])]",
        copy=False,
    )

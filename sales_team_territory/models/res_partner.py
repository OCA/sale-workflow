# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    team_id = fields.Many2one(
        comodel_name="crm.team",
        string="Sales Team",
        compute="_compute_team_id",
        store=True,
        readonly=False,
        precompute=True,
        index="btree_not_null",
        help="Computed from the team territories: state first, then country.",
    )

    @api.depends("state_id", "country_id", "company_id", "parent_id.team_id")
    def _compute_team_id(self):
        Team = self.env["crm.team"]
        for partner in self:
            partner.team_id = (
                Team._get_territory_team(partner)
                or partner.parent_id.team_id
                or partner.team_id
            )

    @api.depends("team_id")
    def _compute_user_id(self):
        res = super()._compute_user_id()
        for partner in self.filtered(lambda p: not p.user_id and p.team_id.user_id):
            partner.user_id = partner.team_id.user_id
        return res

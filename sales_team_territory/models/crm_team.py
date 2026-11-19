# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = "crm.team"

    country_ids = fields.Many2many(
        comodel_name="res.country",
        string="Territory Countries",
        help="Partners located in these countries are assigned to this team.",
    )
    state_ids = fields.Many2many(
        comodel_name="res.country.state",
        string="Territory States",
        help="Partners located in these states are assigned to this team.",
    )

    @api.constrains("country_ids", "state_ids", "company_id")
    def _check_territory_overlap(self):
        for team in self.filtered(lambda t: t.country_ids or t.state_ids):
            domain = [
                ("id", "!=", team.id),
                "|",
                ("state_ids", "in", team.state_ids.ids),
                ("country_ids", "in", team.country_ids.ids),
            ]
            if team.company_id:
                domain.append(("company_id", "in", [False, team.company_id.id]))
            other = self.search(domain, limit=1)
            if other:
                raise ValidationError(
                    self.env._(
                        "The territory of team %(team)s overlaps with team "
                        "%(other)s. A country or state can only belong to one team.",
                        team=team.display_name,
                        other=other.display_name,
                    )
                )

    def _get_territory_team(self, partner):
        """Return the team whose territory matches the partner address.

        A state match wins over a country match. Teams are evaluated in
        their sequence order.
        """
        companies = [False, (partner.company_id or self.env.company).id]
        teams = self.search(
            [
                ("company_id", "in", companies),
                "|",
                ("state_ids", "in", partner.state_id.ids),
                ("country_ids", "in", partner.country_id.ids),
            ]
        )
        by_state = teams.filtered(lambda t: partner.state_id in t.state_ids)
        return by_state[:1] or teams[:1]

    def action_assign_territory_partners(self):
        """Recompute the team of the partners located in this team territory."""
        partners = self.env["res.partner"].search(
            [
                ("parent_id", "=", False),
                "|",
                "|",
                ("team_id", "in", self.ids),
                ("state_id", "in", self.state_ids.ids),
                ("country_id", "in", self.country_ids.ids),
            ]
        )
        partners._compute_team_id()

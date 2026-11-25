# Copyright 2026 ADHOC SA
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class CrmTeamMember(models.Model):
    _inherit = "crm.team.member"

    # Partner access domains (res.partner._access_domain) depend on team membership
    _clear_cache_name = "default"
    _clear_cache_on_fields = frozenset({"user_id", "crm_team_id", "active"})

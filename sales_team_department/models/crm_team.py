# Copyright 2025 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    department_ids = fields.Many2many(
        comodel_name="hr.department",
        string="Departments",
    )

    @api.depends("crm_team_member_ids.active", "department_ids")
    def _compute_member_ids(self):
        res = super()._compute_member_ids()
        for team in self:
            if team.department_ids:
                team.member_ids = team.department_ids.mapped("member_ids.user_id")
        return res

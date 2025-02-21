# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import config


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _check_propagation_allowed(self):
        return bool(
            not config["test_enable"]
            or (config["test_enable"] and self.env.context.get("test_propagation"))
        )

    def write(self, vals):
        """Propagate Salesperson and Sales Channel change in the partner to the
        child contacts, and ensure team_id is inherited from parent_id."""
        if not self._check_propagation_allowed():
            return super().write(vals)
        for record in self:
            if "user_id" in vals:
                childs = record.mapped("child_ids").filtered(
                    lambda child, user=record.user_id: not child.user_id
                    or child.user_id == user
                )
                if childs:
                    childs.write({"user_id": vals["user_id"]})
            if "team_id" in vals:
                childs = record.mapped("child_ids").filtered(
                    lambda child, team=record.team_id: not child.team_id
                    or child.team_id == team
                )
                if childs:
                    childs.write({"team_id": vals["team_id"]})
            if "parent_id" in vals and "team_id" not in vals:
                new_parent = self.browse(vals["parent_id"])
                if new_parent.team_id:
                    vals["team_id"] = new_parent.team_id.id
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure that when a contact is created under a company,
        it inherits the team_id."""
        if not self._check_propagation_allowed():
            return super().create(vals_list)
        for vals in vals_list:
            if "parent_id" in vals:
                if "team_id" not in vals:
                    vals.update(team_id=self.browse(vals["parent_id"]).team_id.id)
        return super().create(vals_list)

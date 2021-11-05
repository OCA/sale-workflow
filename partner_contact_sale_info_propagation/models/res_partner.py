# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

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
        child contacts."""
        if not self._check_propagation_allowed():
            return super().write(vals)
        for record in self:
            if "user_id" in vals:
                childs = record.mapped("child_ids").filtered(
                    lambda r: not r.user_id or r.user_id == record.user_id
                )
                if childs:
                    childs.write({"user_id": vals["user_id"]})
            if "team_id" in vals:
                childs = record.mapped("child_ids").filtered(
                    lambda r: not r.team_id or r.team_id == record.team_id
                )
                if childs:
                    childs.write({"team_id": vals["team_id"]})
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._check_propagation_allowed():
            return super().create(vals_list)
        for vals in vals_list:
            if "parent_id" in vals:
                if "user_id" not in vals:
                    vals.update(user_id=self.browse(vals["parent_id"]).user_id.id)
                if "team_id" not in vals:
                    vals.update(team_id=self.browse(vals["parent_id"]).team_id.id)
        return super().create(vals_list)

    @api.onchange("parent_id")
    def onchange_parent_id(self):
        """Change Salesperson or Sales Channel if the parent company changes
        and there's no Salesperson or Sales Channel defined yet"""
        res = super().onchange_parent_id()
        if self.parent_id and self.parent_id != self:
            parent = self.parent_id
            if not self.user_id:
                res.setdefault("value", {}).update(user_id=parent.user_id)
            if not self.team_id:
                res.setdefault("value", {}).update(team_id=parent.team_id)
        return res

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu,
        )
        if view_type == "form":
            partner_xml = etree.XML(res["arch"])
            partner_fields = partner_xml.xpath("//field[@name='child_ids']")
            if partner_fields:
                partner_field = partner_fields[0]
                context = partner_field.attrib.get("context", "{}").replace(
                    "{", "{'default_user_id': user_id, 'default_team_id': team_id,", 1,
                )
                partner_field.attrib["context"] = context
                res["arch"] = etree.tostring(partner_xml)
        return res

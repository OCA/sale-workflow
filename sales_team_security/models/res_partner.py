# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from lxml import etree

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """
        Patch view to inject the default value for the team_id and user_id.
        """
        # FIXME: Use base_view_inheritance_extension when available
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form":
            eview = etree.fromstring(res["arch"])
            xml_fields = eview.xpath("//field[@name='child_ids']")
            if xml_fields:
                context_str = (
                    xml_fields[0]
                    .get("context", "{}")
                    .replace(
                        "{",
                        "{'default_team_id': team_id, 'default_user_id': user_id,",
                        1,
                    )
                )
                xml_fields[0].set("context", context_str)
            res["arch"] = etree.tostring(eview)
        return res

    @api.onchange("parent_id")
    def _onchange_parent_id_sales_team_security(self):
        """
        If assigning a parent partner and the contact doesn't have
        team, we put the parent's one (if any).
        """
        if self.parent_id and self.parent_id.team_id and not self.team_id:
            self.team_id = self.parent_id.team_id.id

    @api.onchange("user_id")
    def _onchange_user_id_sales_team_security(self):
        if self.user_id.sale_team_id:
            self.team_id = self.user_id.sale_team_id

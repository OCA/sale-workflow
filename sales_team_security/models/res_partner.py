# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from lxml import etree

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # add indexes for better performance on record rules
    user_id = fields.Many2one(index=True)
    team_id = fields.Many2one(index=True)

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """
        Patch view to inject the default value for the team_id and user_id.
        """
        # FIXME: Use base_view_inheritance_extension when available
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu,
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
        """If assigning a parent partner and the contact doesn't have
        team or salesman, we put the parent's one (if any).
        """
        if self.parent_id and self.parent_id.team_id and not self.team_id:
            self.team_id = self.parent_id.team_id.id
        if self.parent_id and self.parent_id.user_id and not self.user_id:
            self.user_id = self.parent_id.user_id.id

    @api.onchange("user_id")
    def _onchange_user_id_sales_team_security(self):
        if self.user_id.sale_team_id:
            self.team_id = self.user_id.sale_team_id

    def _remove_key_followers(self, partner):
        for record in self.mapped("commercial_partner_id"):
            # Look for delivery and invoice addresses
            childrens = record.child_ids.filtered(
                lambda x: x.type in {"invoice", "delivery"}
            )
            (childrens + record).message_unsubscribe(partner_ids=partner.ids)

    def _add_followers_from_salesmans(self):
        """Sync followers in commercial partner + delivery/invoice contacts."""
        for record in self.mapped("commercial_partner_id"):
            followers = (record.child_ids + record).mapped("user_id.partner_id")
            # Look for delivery and invoice addresses
            childrens = record.child_ids.filtered(
                lambda x: x.type in {"invoice", "delivery"}
            )
            (childrens + record).message_subscribe(partner_ids=followers.ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Sync followers on contact creation."""
        records = super().create(vals_list)
        records._add_followers_from_salesmans()
        return records

    def write(self, vals):
        """If the salesman is changed, first remove the old salesman as follower
        of the key contacts (commercial + delivery/invoice), and then sync for
        the new ones.

        It performs as well the followers sync on contact type change.
        """
        if "user_id" in vals:
            for record in self.filtered("user_id"):
                record._remove_key_followers(record.user_id.partner_id)
        result = super().write(vals)
        if "user_id" in vals or vals.get("type") in {"invoice", "delivery"}:
            self._add_followers_from_salesmans()
        return result

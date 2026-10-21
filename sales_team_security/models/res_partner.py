# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import api, fields, models
from odoo.fields import Domain


class ResPartner(models.Model):
    _inherit = "res.partner"

    # add indexes for better performance on record rules
    user_id = fields.Many2one(index=True)

    @api.model
    @api.ormcache("operation", "self.env._access_context")
    def _access_domain(self, operation="read"):
        """Inject extra domain for restricting partners when the user
        has the group 'Sales / User: Own Documents Only'.
        """
        res = super()._access_domain(operation)
        user = self.env.user
        group_my_records = "sales_team.group_sale_salesman"
        group_all_records = "sales_team.group_sale_salesman_all_leads"
        group_team_manager = "sales_team_security.group_sale_team_manager"
        if user.has_group(group_my_records) and not user.has_group(group_all_records):
            domain_followers = Domain(
                [
                    "|",
                    ("message_partner_ids", "in", user.partner_id.ids),
                    ("id", "=", user.partner_id.id),
                ]
            )
            domain_user = Domain([("user_id", "in", [user.id, False])])
            extra_domain = domain_followers | domain_user

            if user.has_group(group_team_manager):
                user_teams = user.crm_team_member_ids.mapped("crm_team_id")
                if user_teams:
                    team_user_ids = user_teams.mapped("crm_team_member_ids.user_id").ids
                    domain_team = Domain([("user_id", "in", team_user_ids)])
                    extra_domain = extra_domain | domain_team

            res = extra_domain & res
        return res

    def _remove_key_followers(self, partner):
        for record in self.mapped("commercial_partner_id"):
            # Look for delivery and invoice addresses
            childrens = record.child_ids.filtered(
                lambda x: x.type in {"invoice", "delivery"}
            )
            (childrens + record).message_unsubscribe(partner_ids=partner.ids)

    def _add_followers_from_salesmen(self):
        """Sync followers in commercial partner + delivery/invoice contacts."""
        for record in self.commercial_partner_id:
            followers = (record.child_ids + record).user_id.partner_id
            # Look for delivery and invoice addresses
            childrens = record.child_ids.filtered(
                lambda x: x.type in {"invoice", "delivery"}
            )
            (childrens + record).message_subscribe(partner_ids=followers.ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Sync followers on contact creation."""
        records = super().create(vals_list)
        records._add_followers_from_salesmen()
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
            self._add_followers_from_salesmen()
        return result

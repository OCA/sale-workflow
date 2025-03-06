# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # add indexes for better performance on record rules
    user_id = fields.Many2one(index=True)

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

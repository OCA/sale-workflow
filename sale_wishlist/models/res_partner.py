# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    wishlists_count = fields.Integer(
        compute="_compute_wishlists_count", string="# Wishlists"
    )

    def _compute_wishlists_count(self):
        # do just one query for all records
        groups = self.env["product.set"]._read_group(
            self._wishlist_domain(), ["partner_id"], ["__count"]
        )
        data_mapped = {partner.id: count for partner, count in groups}
        for rec in self:
            rec.wishlists_count = data_mapped.get(rec.id, 0)

    def _wishlist_domain(self):
        return [("partner_id", "in", self.ids), ("typology", "=", "wishlist")]

    def action_view_wishlists(self):
        self.ensure_one()
        xmlid = "product_set.act_open_product_set_view"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "name": self.env._("Wishlists"),
                "domain": self._wishlist_domain(),
                "context": {
                    "default_typology": "wishlist",
                    "default_partner_id": self.id,
                },
            }
        )
        return action

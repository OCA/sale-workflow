# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        # By default, _message_auto_subscribe_followers adds the user_id of
        # any record inheriting mail.thread to the list of followers.
        # This removes this follower from the auto-subscribed followers.
        # Note: We could have removed `user_id` from `updated_values` and
        # the result would have been the same.
        # However, this method could be overriden somewhere and may use this
        # `user_id` for some reason, which is why I update the result instead.
        res = super()._message_auto_subscribe_followers(
            updated_values, default_subtype_ids
        )
        user_id = updated_values.get("user_id")
        if user_id:
            user = self.env["res.users"].browse(user_id)
            partner = user.partner_id
            res = [follower for follower in res if follower[0] != partner.id]
        return res

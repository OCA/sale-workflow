# Copyright 2024 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_block_id = fields.Many2one(
        comodel_name="sale.delivery.block.reason",
        tracking=True,
        string="Delivery Block Reason",
        compute="_compute_delivery_block_id",
        store=True,
    )

    @property
    def _user_has_auto_done_setting_group(self):
        """Whether the current user has the "auto_done_setting" group."""
        return self.env.user.has_group("sale.group_auto_done_setting")

    @api.constrains("delivery_block_id")
    def _check_not_auto_done(self):
        if self._user_has_auto_done_setting_group and any(
            so.delivery_block_id for so in self
        ):
            raise ValidationError(
                self.env._(
                    'You cannot block a sale order with "auto_done_setting" active.'
                )
            )

    @api.depends("partner_id", "payment_term_id")
    def _compute_delivery_block_id(self):
        """Add the 'Default Delivery Block Reason' if set in the partner
        or in the payment term."""
        for so in self:
            if so._user_has_auto_done_setting_group:
                # Delivery blocks are incompatible with "auto_done_setting"
                # (see _check_not_auto_done), so do not auto-apply any default.
                so.delivery_block_id = False
            elif so.partner_id.default_delivery_block:
                so.delivery_block_id = so.partner_id.default_delivery_block
            else:
                so.delivery_block_id = (
                    so.payment_term_id.default_delivery_block_reason_id or False
                )

    def action_remove_delivery_block(self):
        """Remove the delivery block and create procurements as usual."""
        order_to_unblock = self.filtered(
            lambda so: so.state == "sale" or not so.delivery_block_id
        )
        order_to_unblock.write({"delivery_block_id": False})
        order_to_unblock.order_line._action_launch_stock_rule()
        return True

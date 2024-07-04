# Copyright 2019 Open Source Integrators
# Copyright 2024 Moduon Team
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "tier.validation"]
    _state_from = ["draft", "sent"]
    _state_to = ["sale", "done"]

    _tier_validation_manual_config = False

    def _get_requested_notification_subtype(self):
        return "sale_tier_validation.sale_order_tier_validation_requested"

    def _get_accepted_notification_subtype(self):
        return "sale_tier_validation.sale_order_tier_validation_accepted"

    def _get_rejected_notification_subtype(self):
        return "sale_tier_validation.sale_order_tier_validation_rejected"

    @api.model
    def _user_can_skip_validation(self):
        res = super()._user_can_skip_validation()
        return res or self.env.user.has_group(
            "sale_tier_validation.skip_sale_validations_group"
        )

# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "tier.validation"]
    _state_from = ["draft", "sent", "to approve"]
    _state_to = ["sale", "approved"]

    def _get_requested_notification_subtype(self):
        return "sale_tier_validation.sale_order_tier_validation_requested"

    def _get_accepted_notification_subtype(self):
        return "sale_tier_validation.sale_order_tier_validation_accepted"

    def _get_rejected_notification_subtype(self):
        return "sale_tier_validation.sale_order_tier_validation_rejected"

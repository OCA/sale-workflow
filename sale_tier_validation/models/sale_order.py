# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


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

    def _get_fields_to_write_validation(self, vals, records_exception_function):
        # Don't block order validation when sale_loyalty is installed and no coupon
        # is being handled, due to this code assigning always an empty value:
        # https://github.com/odoo/odoo/blob/2a7876538e9ea630563e39ee8402b27147d1e428/
        # addons/sale_loyalty/models/sale_order.py#L740
        # Done here for not creating a glue module as we can detect the situation. The
        # only drawback is that this doesn't have any regression test
        (
            allowed_field_names,
            not_allowed_field_names,
        ) = super()._get_fields_to_write_validation(vals, records_exception_function)
        if "applied_coupon_ids" in vals and not vals.get("applied_coupon_ids"):
            allowed_field_names += ["applied_coupon_ids"]
        return allowed_field_names, not_allowed_field_names

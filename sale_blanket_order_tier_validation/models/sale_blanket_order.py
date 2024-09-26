# Copyright 2024 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleBlanketOrder(models.Model):
    """
    Adding tier validation functionality to Blanket Orders.
    """

    _name = "sale.blanket.order"
    _inherit = ["sale.blanket.order", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["open", "done", "expired"]

    _tier_validation_manual_config = False
    _tier_validation_state_field_is_computed = True

    @api.model
    def _get_after_validation_exceptions(self):
        return super()._get_after_validation_exceptions() + [
            "confirmed",
            "name",
        ]

    @api.model
    def _get_under_validation_exceptions(self):
        return super()._get_under_validation_exceptions() + [
            "confirmed",
            "name",
        ]

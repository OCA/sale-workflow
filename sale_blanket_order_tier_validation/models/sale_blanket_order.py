# Copyright 2024 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import float_is_zero


class SaleBlanketOrder(models.Model):
    """
    Adding tier validation functionality to Blanket Orders.
    """

    _name = "sale.blanket.order"
    _inherit = ["sale.blanket.order", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["open", "done", "expired"]

    _tier_validation_manual_config = False

    @api.depends(
        "line_ids.remaining_uom_qty",
        "validity_date",
        "confirmed",
    )
    def _compute_state(self):
        """Complete override of Blanket Order Compute State Method:
        The OCA Blanket Order module sets state via compute method which messes
        with tier validation checks so we are going to instead set the state
        to 'Open' only when clicking confirmed. This also forces process as before
        just changing data would reset BO back to Open if expired."""
        today = fields.Date.today()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for order in self:
            if not order.confirmed:
                order.state = "draft"
            elif order.validity_date <= today:
                order.state = "expired"
            elif float_is_zero(
                sum(
                    order.line_ids.filtered(lambda line: not line.display_type).mapped(
                        "remaining_uom_qty"
                    )
                ),
                precision_digits=precision,
            ):
                order.state = "done"
            # Removing else statement from original method
            # else:
            #     order.state = "open"

    def action_confirm(self):
        """Set the state to 'Open' when clicking confirmed instead of during compute."""
        for rec in self:
            rec.write({"state": "open"})
        return super().action_confirm()

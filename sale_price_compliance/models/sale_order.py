# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, exceptions, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        res = super()._action_confirm()
        self._check_compliant_pricing()
        return res

    def _check_compliant_pricing(self):
        """Check if lines are in compliant state"""
        is_sale_manager = self.env.user.has_group("sales_team.group_sale_manager")
        for record in self:
            # Check all lines are in compliant state
            non_compliant_lines = record.order_line.filtered_domain(
                [("price_compliance_tier", "=", "non_compliant")]
            )
            if not non_compliant_lines:
                continue
            # If user is a Sales manager, skip this check
            if is_sale_manager:
                record.message_post(
                    body=_(
                        "Order confirmed with Non Compliant prices by %s.",
                        self.env.user.name,
                    )
                )
                continue
            raise exceptions.UserError(
                _(
                    "The order contains lines with non-compliant prices.\n"
                    "Please review the prices before confirming the order or "
                    "contact your sales manager for further assistance."
                )
            )

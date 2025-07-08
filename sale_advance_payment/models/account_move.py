# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        # Automatic reconciliation of payment when invoice confirmed.
        res = super().action_post()
        for move in self:
            sale_order = move.mapped("line_ids.sale_line_ids.order_id")
            if not sale_order:
                continue

            # Get payment move IDs first
            payment_move_ids = sale_order.account_payment_ids.move_id.ids
            if not payment_move_ids:
                continue

            # Domain search (most efficient for large datasets)
            advance_payment_lines = self.env["account.move.line"].search(
                [
                    ("move_id", "in", payment_move_ids),
                    (
                        "account_id.account_type",
                        "in",
                        ("asset_receivable", "liability_payable"),
                    ),
                    ("reconciled", "=", False),
                    ("parent_state", "=", "posted"),
                ]
            )

            for line in advance_payment_lines:
                move.js_assign_outstanding_line(line_id=line.id)
        return res

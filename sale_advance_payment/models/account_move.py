# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        posted._reconcile_sale_advance_payments()
        return posted

    def _reconcile_sale_advance_payments(self):
        invoices = self.filtered(lambda m: m.is_invoice(include_receipts=True))
        sale_orders = invoices.line_ids.sale_line_ids.order_id
        all_payment_move_ids = sale_orders.account_payment_ids.move_id.ids
        if not all_payment_move_ids:
            return
        all_payment_lines = self.env["account.move.line"].search(
            [
                ("move_id", "in", all_payment_move_ids),
                (
                    "account_id.account_type",
                    "in",
                    ("asset_receivable", "liability_payable"),
                ),
                ("reconciled", "=", False),
                ("parent_state", "=", "posted"),
            ]
        )
        for move in invoices:
            sale_order = move.line_ids.sale_line_ids.order_id
            payment_move_ids = sale_order.account_payment_ids.move_id.ids
            if not payment_move_ids:
                continue
            term_accounts = move.line_ids.filtered(
                lambda line: line.display_type == "payment_term"
            ).account_id
            payment_lines = all_payment_lines.filtered(
                lambda x, move_ids=payment_move_ids, accounts=term_accounts: (
                    x.move_id.id in move_ids
                    and x.account_id in accounts
                    and not x.reconciled
                )
            )
            for line in payment_lines:
                if move.currency_id.is_zero(move.amount_residual):
                    break
                move.js_assign_outstanding_line(line_id=line.id)

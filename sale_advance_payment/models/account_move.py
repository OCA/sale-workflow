# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        # Automatic reconciliation of payment when invoice confirmed.
        res = super()._post(soft=soft)
        for invoice in self:
            # Get Advance Payment Account Moves
            sale_orders = invoice.mapped("line_ids.sale_line_ids.order_id")
            advance_payment_moves = sale_orders.account_payment_ids.move_id
            # Get reconcilable payments JSON data
            widget_json = invoice.invoice_outstanding_credits_debits_widget or {}
            can_reconcile_lines = filter(
                lambda x: x.get("move_id") in advance_payment_moves.ids,
                widget_json.get("content", []),
            )
            for line in can_reconcile_lines:
                invoice.js_assign_outstanding_line(line_id=line.get("id"))
        return res

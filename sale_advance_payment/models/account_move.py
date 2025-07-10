# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        # Automatic reconciliation of payment when invoice confirmed.
        res = super(AccountMove, self)._post(soft=soft)
        for move in self:
            sale_order = move.mapped("line_ids.sale_line_ids.order_id")
            if (
                not sale_order
                or move.invoice_outstanding_credits_debits_widget is False
            ):
                continue
            json_invoice_outstanding_data = (
                move.invoice_outstanding_credits_debits_widget.get("content", [])
            )
            for data in json_invoice_outstanding_data:
                if data.get("move_id") in sale_order.account_payment_ids.move_id.ids:
                    move.js_assign_outstanding_line(line_id=data.get("id"))
        return res

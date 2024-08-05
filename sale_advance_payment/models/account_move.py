# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        # Automatic reconciliation of payment when invoice confirmed.
        res = super().action_post()
        sale_order = self.mapped("line_ids.sale_line_ids.order_id")
        if sale_order and self.invoice_outstanding_credits_debits_widget is not False:
            json_invoice_outstanding_data = (
                self.invoice_outstanding_credits_debits_widget.get("content", [])
            )
            for data in json_invoice_outstanding_data:
                if data.get("move_id") in sale_order.account_payment_ids.move_id.ids:
                    self.js_assign_outstanding_line(line_id=data.get("id"))
        return res

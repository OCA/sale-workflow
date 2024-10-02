# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    payment_transaction_count = fields.Integer(
        string="Number of payment transactions",
        compute="_compute_payment_transaction_count",
    )

    @api.depends("transaction_ids")
    def _compute_payment_transaction_count(self):
        for rec in self:
            rec.payment_transaction_count = len(rec.transaction_ids)

    def action_view_transaction(self):
        action = {
            "type": "ir.actions.act_window",
            "name": "Payment Transactions",
            "res_model": "payment.transaction",
        }
        if self.payment_transaction_count == 1:
            action.update({"res_id": self.transaction_ids.id, "view_mode": "form"})
        else:
            action.update(
                {
                    "view_mode": "tree,form",
                    "domain": [("id", "in", self.transaction_ids.ids)],
                }
            )
        return action

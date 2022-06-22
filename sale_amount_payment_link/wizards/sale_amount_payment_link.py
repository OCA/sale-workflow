# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class SalePaymentLink(models.TransientModel):
    _inherit = "payment.link.wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res["res_id"] and res["res_model"] == "sale.order":
            record = self.env[res["res_model"]].browse(res["res_id"])
            transactions = record.transaction_ids.filtered(lambda x: x.state == "done")
            if transactions and not record.invoice_ids:
                payments = [transac.payment_id.id for transac in transactions]
                invoice_ids = self.env["account.move"].search(
                    [("payment_id", "in", payments)]
                )
                paid_amount = sum(
                    invoice_ids.filtered(lambda x: x.state != "cancel").mapped(
                        "amount_total"
                    )
                )
                res.update({"amount": record.amount_total - paid_amount})
        return res

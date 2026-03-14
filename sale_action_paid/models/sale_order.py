# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models, tools
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_paid_get_transaction(self):
        self.ensure_one()
        txs = self.sudo().transaction_ids.filtered(
            lambda t: t.state in ("draft", "pending")
        )
        if not txs:
            return
        tx = txs._get_last()
        if not tx:
            tx = txs.sorted()[:1]
        return tx

    def _action_paid_create_transaction(self, **values):
        order = fields.first(self)
        default_values = {
            "amount": order.amount_total,
            "currency_id": order.currency_id.id,
            "provider_id": self.env.ref("payment.payment_provider_transfer").id,
            "operation": "offline",
            "partner_id": order.partner_id.id,
            "partner_lang": order.partner_id.lang,
            "sale_order_ids": [Command.set(self.ids)],
        }
        transaction_vals = dict(default_values, **values)
        if not transaction_vals.get("payment_method_id"):
            # default to Wire transfer
            method = self.env.ref(
                "payment_custom.payment_method_wire_transfer", raise_if_not_found=False
            )
            if not method and tools.config["test_enable"]:
                method = self.env.ref("payment.payment_method_unknown")
            if not method:
                raise UserError(
                    self.env._(
                        "Cannot mark as paid as there are no pending transaction. "
                        "Install payment_custom module to allow the creation of a "
                        "transaction."
                    )
                )
            transaction_vals["payment_method_id"] = method.id
        tx = self.env["payment.transaction"].sudo().create(transaction_vals)
        return tx

    @api.model
    def _action_paid(self, tx, force_invoice=False):
        tx._set_done()
        # Prevent to generate a new payment for marking the invoice as paid.
        # This will disable the send_payment_succeeded_for_order_mail,
        # auto invoice, invoice sending.
        tx.operation = "validation"
        tx._check_amount_and_confirm_order()
        tx._post_process()
        if not tx.invoice_ids and force_invoice:
            # if auto invoice is not enabled, force invoice creation
            tx._invoice_sale_orders()
        tx.invoice_ids.filtered(lambda inv: inv.state == "draft").action_post()
        tx.is_post_processed = True

    def action_paid(self):
        for order in self.filtered(lambda so: so.state in ("draft", "sent")):
            tx = order._action_paid_get_transaction()
            if not tx:
                tx = order._action_paid_create_transaction()
            order._action_paid(tx)

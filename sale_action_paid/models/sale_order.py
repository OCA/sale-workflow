# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import str2bool


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
    def _action_paid(self, tx, auto_invoice=True):
        tx._set_done()
        # Prevent to generate a new payment for marking the invoice as paid.
        # This will disable the send_payment_succeeded_for_order_mail,
        # auto invoice, invoice sending.
        tx.operation = "validation"
        tx._post_process()
        tx._check_amount_and_confirm_order()
        # recover invoice creation to allow manual payment reconciliation
        if auto_invoice:
            # Invoice the sales orders of confirmed transactions
            # instead of only confirmed orders to create the invoice
            # even if only a partial payment was made.
            tx._invoice_sale_orders()
            tx.invoice_ids.filtered(lambda inv: inv.state == "draft").action_post()
        tx.is_post_processed = True

    def action_paid(self):
        auto_invoice = str2bool(
            self.env["ir.config_parameter"].sudo().get_param("sale.automatic_invoice")
        )
        for order in self.filtered(lambda so: so.state in ("draft", "sent")):
            tx = order._action_paid_get_transaction()
            if not tx:
                tx = order._action_paid_create_transaction()
            order._action_paid(tx, auto_invoice=auto_invoice)

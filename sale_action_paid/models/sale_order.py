# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, tools


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

    def _action_paid(self, force_invoice=False):
        self.ensure_one()
        tx = self._action_paid_get_transaction()
        if tx:
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
            return tx.invoice_ids
        if self.state in ("draft", "sent"):
            self.with_context(send_email=True).action_confirm()
        if force_invoice:
            self._force_lines_to_invoice_policy_order()
            invoice = self._create_invoices(final=True)
            invoice.action_post()
            if not self.env.context.get("skip_sale_auto_invoice_send"):
                invoice.is_move_sent = True
                send_context = {"allow_raising": False, "allow_fallback_pdf": True}
                self.env["account.move.send"]._generate_and_send_invoices(
                    invoice,
                    **send_context,
                )
            return invoice
        return self.env["account.move"]

    def action_paid(self):
        auto_invoice = tools.str2bool(
            self.env["ir.config_parameter"].sudo().get_param("sale.automatic_invoice")
        )
        for order in self.filtered(lambda so: so.state in ("draft", "sent")):
            order._action_paid(force_invoice=auto_invoice)

# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.tools import str2bool


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_paid(self):
        auto_invoice = str2bool(
            self.env["ir.config_parameter"].sudo().get_param("sale.automatic_invoice")
        )
        for order in self.filtered(lambda so: so.state in ("draft", "sent")):
            txs = order.sudo().transaction_ids.filtered(
                lambda t: t.state in ("draft", "pending")
            )
            tx = txs._get_last()
            if not tx:
                tx = txs.sorted()[:1]
            if tx:
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
                    tx.invoice_ids.filtered(
                        lambda inv: inv.state == "draft"
                    ).action_post()
                tx.is_post_processed = True

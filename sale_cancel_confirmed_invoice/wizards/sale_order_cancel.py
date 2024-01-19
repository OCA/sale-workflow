# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderCancel(models.TransientModel):

    _inherit = "sale.order.cancel"

    sale_cancel_confirmed_invoice = fields.Boolean(
        compute="_compute_sale_cancel_confirmed_invoice"
    )

    @api.depends("order_id")
    @api.depends_context("company")
    def _compute_sale_cancel_confirmed_invoice(self):
        self.sale_cancel_confirmed_invoice = (
            self.env.company.enable_sale_cancel_confirmed_invoice
        )

    def action_cancel(self):
        if self.env.company.enable_sale_cancel_confirmed_invoice:
            invoices = self.order_id.invoice_ids.filtered(
                lambda i: i.state == "posted" and i.payment_state == "not_paid"
            )
            invoices.button_draft()
            invoices.button_cancel()
        return super(SaleOrderCancel, self).action_cancel()

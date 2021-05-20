# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_blocking_reason_id = fields.Many2one(
        "invoice.blocking.reason",
        string="Blocking for invoicing",
    )

    @api.depends("invoice_blocking_reason_id", "state", "order_line.invoice_status")
    def _get_invoice_status(self):
        super()._get_invoice_status()
        for order in self.filtered(
            lambda order: order.invoice_blocking_reason_id
            and order.state in ("sale", "done")
        ):
            order.invoice_status = "no"

    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        if self.invoice_blocking_reason_id:
            return self.env["sale.order.line"]

        return super()._get_invoiceable_lines(final=final)

    @api.model
    def _nothing_to_invoice_error(self):
        error = super()._nothing_to_invoice_error()
        msg = [x for x in error.args]

        msg.append(
            _(
                """
- You may have an invoice blocking reason on the sale order
        """
            )
        )
        return UserError(msg)

# Copyright 2026 OBS Solutions B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models

PAID_STATES = {"paid", "invoicing_legacy"}
UNPAID_STATES = {"not_paid", "blocked"}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_payment_state = fields.Selection(
        selection=[
            ("no_invoice", "No Invoice"),
            ("not_paid", "Not Paid"),
            ("partial", "Partially Paid"),
            ("in_payment", "In Payment"),
            ("paid", "Paid"),
        ],
        string="Payment Status",
        compute="_compute_invoice_payment_state",
        store=True,
        copy=False,
        help="Payment status of the posted customer invoices and credit notes "
        "of this order. Draft invoices and fully reversed invoices are ignored. "
        "It does not tell whether the order is fully invoiced: check the "
        "Invoice Status for that.",
    )
    invoice_amount_residual = fields.Monetary(
        string="Amount Due",
        compute="_compute_invoice_payment_state",
        store=True,
        copy=False,
        currency_field="currency_id",
        groups="account.group_account_invoice,account.group_account_readonly",
        help="Open amount of the posted customer invoices minus the open "
        "amount of the posted credit notes of this order.",
    )

    @api.depends(
        "currency_id",
        "order_line.invoice_lines.move_id.state",
        "order_line.invoice_lines.move_id.payment_state",
        "order_line.invoice_lines.move_id.amount_residual",
        "order_line.invoice_lines.move_id.currency_id",
        "order_line.invoice_lines.move_id.reversed_entry_id",
    )
    def _compute_invoice_payment_state(self):
        for order in self:
            moves = order._get_payment_state_moves()
            order.invoice_payment_state = order._get_invoice_payment_state(
                set(moves.mapped("payment_state"))
            )
            order.invoice_amount_residual = sum(
                order._get_move_residual_in_order_currency(move) for move in moves
            )

    def _get_payment_state_moves(self):
        """Return the posted customer invoices and credit notes to consider.

        Fully reversed invoices and the credit notes reversing them cancel
        each other out, so both are left out.
        """
        self.ensure_one()
        moves = self.order_line.invoice_lines.move_id.filtered(
            lambda move: move.state == "posted" and move.is_sale_document()
        )
        reversed_moves = moves.filtered(lambda move: move.payment_state == "reversed")
        return moves.filtered(
            lambda move: move not in reversed_moves
            and move.reversed_entry_id not in reversed_moves
        )

    @api.model
    def _get_invoice_payment_state(self, payment_states):
        """Map the payment states of the invoices to a single order state.

        :param set payment_states: ``payment_state`` values of the invoices
        :return: a value of the ``invoice_payment_state`` selection
        """
        if not payment_states:
            return "no_invoice"
        if payment_states <= PAID_STATES:
            return "paid"
        if payment_states <= PAID_STATES | {"in_payment"}:
            return "in_payment"
        if payment_states <= UNPAID_STATES:
            return "not_paid"
        return "partial"

    def _get_move_residual_in_order_currency(self, move):
        """Return the signed open amount of ``move`` in the order currency."""
        self.ensure_one()
        amount = move.amount_residual
        if move.move_type == "out_refund":
            amount = -amount
        if move.currency_id != self.currency_id:
            amount = move.currency_id._convert(
                amount,
                self.currency_id,
                self.company_id,
                move.invoice_date or move.date,
            )
        return amount

# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    down_payment_deduction = fields.Selection(
        selection=[
            ("full", "Deduct full down payment"),
            ("partial", "Deduct partial down payment"),
        ],
        default="full",
        required=True,
        help="Choose whether to deduct the full down payment or a partial amount.",
    )

    total_deduction_amount = fields.Monetary(
        string="Total Deduction",
        help="Total amount available for down payment deduction.",
        compute="_compute_total_deduction_amount",
    )

    deduction_amount = fields.Monetary(
        string="Deduction",
        help="Specify the amount to deduct from the down payment if partial "
        "deduction is selected.",
        compute="_compute_deduction_amount",
        readonly=False,
        store=True,
    )

    @api.constrains("deduction_amount")
    def _check_deduction_amount(self):
        for wizard in self:
            if wizard.down_payment_deduction == "partial":
                if wizard.deduction_amount > wizard.total_deduction_amount:
                    raise ValidationError(
                        self.env._(
                            "The deduction amount cannot exceed the total "
                            "available down payment deduction."
                        )
                    )

    @api.depends("sale_order_ids")
    def _compute_total_deduction_amount(self):
        # Separated into two methods to avoid recomputing when the other one is changed
        # Although it's the same logic, one field is readonly and the other is editable
        for wizard in self:
            dp_lines = wizard.sale_order_ids.mapped("order_line").filtered(
                lambda lin: lin.is_downpayment
            )
            total_remaining = sum(lin.qty_invoiced * lin.price_unit for lin in dp_lines)
            wizard.total_deduction_amount = total_remaining

    @api.depends("sale_order_ids")
    def _compute_deduction_amount(self):
        for wizard in self:
            dp_lines = wizard.sale_order_ids.mapped("order_line").filtered(
                lambda lin: lin.is_downpayment
            )
            total_remaining = sum(lin.qty_invoiced * lin.price_unit for lin in dp_lines)
            wizard.deduction_amount = total_remaining

    def _create_invoices(self, sale_orders):
        # Override to adjust down payment deduction before creating invoices
        # Only run if partial deduction is selected
        if self.down_payment_deduction == "partial" and self.deduction_amount:
            for order in self.sale_order_ids:
                dp_lines = order.order_line.filtered("is_downpayment")
                total_dp_remaining = sum(
                    lin.qty_invoiced * lin.price_unit for lin in dp_lines
                )
                # Deduct only up to the available amount
                to_deduct = min(self.deduction_amount, total_dp_remaining)
                order._adjust_downpayment_lines(to_deduct)
        res = super()._create_invoices(sale_orders)
        # Recompute qty_to_invoice to reflect changes, after invoice creation
        # since by adjusting the down payment lines we modified it
        self.sale_order_ids.order_line._compute_qty_to_invoice()
        return res

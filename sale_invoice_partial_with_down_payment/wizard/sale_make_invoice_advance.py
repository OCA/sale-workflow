# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    downpayment_exceeds_delivery = fields.Boolean(
        compute="_compute_downpayment_info",
        string="Down Payment Exceeds Delivery",
    )
    delivered_ratio = fields.Float(
        compute="_compute_downpayment_info",
        digits=(16, 4),
    )
    proportional_downpayment_amount = fields.Monetary(
        compute="_compute_downpayment_info",
        string="Proportional Down Payment Deduction",
        currency_field="currency_id",
        help="Down payment amount to deduct on this invoice if "
        "handling is proportional.",
    )
    total_downpayment_invoiced = fields.Monetary(
        compute="_compute_downpayment_info",
        string="Total Down Payment Invoiced",
        currency_field="currency_id",
    )
    downpayment_handling = fields.Selection(
        selection=[
            (
                "proportional",
                "Regular invoice with proportional down payment deduction",
            ),
            ("fixed", "Regular invoice with fixed amount down payment deduction"),
            ("credit_note", "Credit Note (native behaviour)"),
        ],
        string="Down Payment Handling",
        default="proportional",
        help=(
            "- Proportional: deduct the share of the DP proportional "
            "to this delivery.\n"
            "- Fixed: deduct a specific amount you enter manually.\n"
            "- Credit Note: native Odoo behaviour."
        ),
    )
    downpayment_fixed_amount = fields.Monetary(
        string="Down Payment Amount to Deduct",
        currency_field="currency_id",
        compute="_compute_downpayment_fixed_amount",
        inverse="_inverse_downpayment_fixed_amount",
        readonly=False,
        help=(
            "Amount to deduct as down payment on this invoice when "
            "handling is 'Fixed'."
        ),
    )

    def _dp_line_is_posted(self, line):
        return (
            line.is_downpayment
            and not line.display_type
            and any(
                inv_line.move_id.state == "posted"
                and inv_line.move_id.move_type == "out_invoice"
                for inv_line in line.invoice_lines
            )
        )

    @api.depends("sale_order_ids", "advance_payment_method")
    def _compute_downpayment_info(self):
        for wizard in self:
            if wizard.advance_payment_method != "delivered":
                wizard.downpayment_exceeds_delivery = False
                wizard.delivered_ratio = 0.0
                wizard.proportional_downpayment_amount = 0.0
                wizard.total_downpayment_invoiced = 0.0
                continue
            (
                wizard.downpayment_exceeds_delivery,
                wizard.delivered_ratio,
                wizard.proportional_downpayment_amount,
                wizard.total_downpayment_invoiced,
            ) = wizard._get_downpayment_info(wizard.sale_order_ids)

    def _get_downpayment_info(self, orders):
        total_dp_invoiced = 0.0
        total_deliverable = 0.0
        total_ordered = 0.0

        for order in orders:
            for line in order.order_line:
                if line.display_type:
                    continue
                if line.is_downpayment:
                    if self._dp_line_is_posted(line):
                        total_dp_invoiced += line.price_unit
                else:
                    total_ordered += line.price_subtotal
                    if line.qty_to_invoice > 0:
                        total_deliverable += line.untaxed_amount_to_invoice

        if not total_dp_invoiced or not total_ordered:
            return False, 0.0, 0.0, 0.0

        ratio = total_deliverable / total_ordered
        proportional_amount = total_dp_invoiced * ratio
        exceeds = total_deliverable < total_dp_invoiced

        return exceeds, ratio, proportional_amount, total_dp_invoiced

    @api.depends("downpayment_handling", "proportional_downpayment_amount")
    def _compute_downpayment_fixed_amount(self):
        for wizard in self:
            wizard.downpayment_fixed_amount = 0.0
            if wizard.downpayment_handling == "fixed":
                wizard.downpayment_fixed_amount = wizard.proportional_downpayment_amount

    def _inverse_downpayment_fixed_amount(self):
        for wizard in self:
            if wizard.downpayment_handling != "fixed":
                continue
            if wizard.downpayment_fixed_amount < 0:
                raise ValidationError(
                    _("The down payment deduction amount cannot be negative.")
                )
            if wizard.downpayment_fixed_amount > wizard.total_downpayment_invoiced:
                raise ValidationError(
                    _(
                        "The down payment deduction (%(amount)s) cannot exceed "
                        "the total down payment invoiced (%(total)s).",
                        amount=wizard.downpayment_fixed_amount,
                        total=wizard.total_downpayment_invoiced,
                    )
                )

    def _create_invoices(self, sale_orders):
        if (
            self.advance_payment_method != "delivered"
            or not self.downpayment_exceeds_delivery
            or self.downpayment_handling not in ("proportional", "fixed")
        ):
            return super()._create_invoices(sale_orders)

        if self.downpayment_handling == "proportional":
            amount = self.delivered_ratio
        else:
            amount = self.downpayment_fixed_amount
        ctx = {
            "downpayment_amount": amount,
            "downpayment_handling": self.downpayment_handling,
        }

        return sale_orders.with_context(**ctx)._create_invoices(
            final=self.deduct_down_payments,
            grouped=not self.consolidated_billing,
        )

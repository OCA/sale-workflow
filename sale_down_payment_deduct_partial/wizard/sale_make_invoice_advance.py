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
                lambda line: line.is_downpayment
            )
            total_remaining = 0.0
            for line in dp_lines:
                res = line.tax_id.compute_all(
                    line.price_unit,
                    currency=line.order_id.currency_id,
                    quantity=line.qty_invoiced,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )
                total_remaining += res["total_included"]
            wizard.total_deduction_amount = total_remaining

    @api.depends("sale_order_ids")
    def _compute_deduction_amount(self):
        for wizard in self:
            dp_lines = wizard.sale_order_ids.mapped("order_line").filtered(
                lambda line: line.is_downpayment
            )
            total_remaining = 0.0
            for line in dp_lines:
                res = line.tax_id.compute_all(
                    line.price_unit,
                    currency=line.order_id.currency_id,
                    quantity=line.qty_invoiced,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )
                total_remaining += res["total_included"]
            wizard.deduction_amount = total_remaining

    def _create_invoices(self, sale_orders):
        # Override to adjust down payment deduction before creating invoices
        # Only run if partial deduction is selected
        if self.down_payment_deduction == "partial" and self.deduction_amount:
            for order in self.sale_order_ids:
                dp_lines = order.order_line.filtered(
                    lambda line: line.is_downpayment
                    and not line.display_type == "line_section"
                )
                total_dp_remaining = 0.0
                for lin in dp_lines:
                    res = lin.tax_id.compute_all(
                        lin.price_unit,
                        currency=lin.order_id.currency_id,
                        quantity=lin.qty_invoiced,
                        product=lin.product_id,
                        partner=lin.order_id.partner_shipping_id,
                    )
                    total_dp_remaining += res["total_included"]
                # Deduct only up to available total (tax included)
                to_deduct_incl = min(self.deduction_amount, total_dp_remaining)
                # Convert to tax-excluded base before adjusting
                # Assume consistent tax rate on downpayment lines
                if dp_lines:
                    line = dp_lines[0]
                    taxes_res = line.tax_id.compute_all(
                        1.0,
                        currency=line.order_id.currency_id,
                        quantity=1.0,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id,
                    )
                    tax_ratio = (
                        taxes_res["total_excluded"] / taxes_res["total_included"]
                        if taxes_res["total_included"]
                        else 1.0
                    )
                    to_deduct_excl = to_deduct_incl * tax_ratio
                else:
                    to_deduct_excl = to_deduct_incl
                order._adjust_downpayment_lines(to_deduct_excl)
        invoices = super()._create_invoices(
            sale_orders.with_context(skip_downpayment_final_fix=True)
        )
        self.sale_order_ids.order_line._compute_qty_to_invoice()
        return invoices

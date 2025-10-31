# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.float_utils import float_compare, float_is_zero


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _adjust_downpayment_lines(self, amount):
        # Adjust the down payment lines to deduct only the specified amount
        # Set the qty_to_invoice on down payment lines accordingly
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get("Account")
        remaining = amount
        dp_lines = self.order_line.filtered(
            lambda line: line.is_downpayment and not line.display_type
        )
        for line in dp_lines:
            if float_compare(remaining, 0.0, precision_digits=precision) == 0:
                line.qty_to_invoice = 0.0
                continue
            # Compute total (tax-excluded) value for this line
            res = line.tax_id.compute_all(
                line.price_unit,
                currency=line.order_id.currency_id,
                quantity=line.qty_invoiced,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            line_total_excl = res["total_excluded"]
            if float_is_zero(
                line_total_excl, precision_rounding=line.currency_id.rounding
            ):
                continue
            if (
                float_compare(remaining, line_total_excl, precision_digits=precision)
                >= 0
            ):
                line.qty_to_invoice = -line.qty_invoiced
                remaining -= line_total_excl
            else:
                # Partial deduction: proportionate to remaining amount
                proportion = remaining / line_total_excl
                qty_to_invoice = -(line.qty_invoiced * proportion)
                line.qty_to_invoice = qty_to_invoice
                remaining = 0.0
        if (
            float_compare(
                abs(remaining), self.currency_id.rounding, precision_digits=precision
            )
            == -1
        ):
            remaining = 0.0

    def down_payment_final_rounding(self, final):
        # Avoid down payment lines rounding
        # because that will make incorrect tax lines
        if self.env.context.get("skip_downpayment_final_fix", False):
            return False
        return super().down_payment_final_rounding(final)

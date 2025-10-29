# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _adjust_downpayment_lines(self, amount):
        # Adjust the down payment lines to deduct only the specified amount
        # Set the qty_to_invoice on down payment lines accordingly
        self.ensure_one()
        remaining = amount
        # Only consider down payment lines (and not section lines)
        dp_lines = self.order_line.filtered(
            lambda lin: lin.is_downpayment and not lin.display_type
        )
        for line in dp_lines:
            line_remaining_qty = line.qty_invoiced
            line_total = line_remaining_qty * line.price_unit
            if remaining == 0:  # No more amount to deduct
                line.qty_to_invoice = 0.0
            elif remaining >= line_total:  # Deduct full line
                line.qty_to_invoice = -line_remaining_qty
                remaining -= line_total
            elif remaining < line_total:  # Deduct partial line
                # Calculate the proportion of the line to deduct
                # quantity to invoice = -(remaining amount / price unit)
                # since the original invoiced qty in down payment lines is 1
                proportion = remaining / line.price_unit
                line.qty_to_invoice = -proportion
                remaining = 0.0

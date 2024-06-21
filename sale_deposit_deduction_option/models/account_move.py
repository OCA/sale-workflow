# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        amount_so = self.env.context.get("amount_so", 0.0)
        if (
            self.env.context.get("deposit_deduction_option") == "proportional"
            and amount_so
        ):
            for move in moves:
                inv_lines = move.invoice_line_ids.filtered(lambda x: x.quantity > 0)
                adv_lines = move.invoice_line_ids.filtered(lambda x: x.quantity < 0)
                inv_untaxed = sum(inv_lines.mapped("price_subtotal"))
                prop = inv_untaxed / amount_so
                # if inv_untaxed is zero, nothing to do
                if not prop:
                    continue
                for line in adv_lines:
                    line.with_context(check_move_validity=False).write(
                        {"quantity": max(-prop, line.quantity)}
                    )
                # Update line
                move.with_context(
                    check_move_validity=False
                )._move_autocomplete_invoice_lines_values()
        return moves

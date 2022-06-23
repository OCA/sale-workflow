# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _name = "account.move"
    _description = "Account Move"
    _inherit = ["account.move", "price.include.tax.mixin"]

    @api.depends(
        "invoice_line_ids.tax_ids.price_include",
    )
    def _compute_price_tax_state(self):
        return super()._compute_price_tax_state()

    def action_post(self):
        for move in self:
            if (
                move.move_type
                in ["out_invoice", "in_invoice", "out_refund", "in_refund"]
                and move.price_tax_state == "exception"
            ):
                raise UserError(
                    _(
                        "Invoice lines must have the same kind of taxes "
                        "(price include or exclude)."
                    )
                )
        return super().action_post()

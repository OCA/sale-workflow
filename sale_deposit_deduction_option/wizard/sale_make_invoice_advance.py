# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    deposit_deduction_option = fields.Selection(
        [
            ("full", "Deduct Full Deposit"),
            ("proportional", "Deduct Deposit Proportionally"),
            ("no", "No Deduct"),
        ],
        default="full",
        required=True,
    )

    @api.onchange("deposit_deduction_option")
    def _onchange_deposit_deduction_option(self):
        self.deduct_down_payments = self.deposit_deduction_option != "no"

    def create_invoices(self):
        if self.deposit_deduction_option == "proportional":
            sale_orders = self.env["sale.order"].browse(
                self._context.get("active_ids", [])
            )
            self = self.with_context(
                deposit_deduction_option=self.deposit_deduction_option,
                amount_so=sum(sale_orders.mapped("amount_untaxed")),
            )
        return super().create_invoices()

# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_vals):
        res = super()._prepare_invoice_line(**optional_vals)
        fixed_or_proportional = self.env.context.get("downpayment_handling")
        amount = self.env.context.get("downpayment_amount")
        if not fixed_or_proportional or not amount or not self.is_downpayment:
            return res

        if fixed_or_proportional == "proportional":
            res["quantity"] = -amount
            res["name"] = _(
                "Down payment deduction (%(pct).1f%% of %(order)s)",
                pct=amount * 100,
                order=self.order_id.name,
            )
        else:
            res["quantity"] = -(amount / self.price_unit) if self.price_unit else 0.0
            res["name"] = _(
                "Down payment deduction (%(amount)s of %(order)s)",
                amount=self.order_id.currency_id.format(amount),
                order=self.order_id.name,
            )
        return res

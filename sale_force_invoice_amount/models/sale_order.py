from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "state",
        "invoice_ids",
        "invoice_ids.amount_total_in_currency_signed",
        "amount_total",
        "invoice_ids.state",
        "force_invoiced",
    )
    def _compute_invoice_amount(self):
        res = super()._compute_invoice_amount()

        for order in self:
            if order.force_invoiced:
                order.invoiced_amount = order.amount_total
                order.uninvoiced_amount = 0.0
        return res

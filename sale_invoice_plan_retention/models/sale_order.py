# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_retention = fields.Selection(
        selection=[("percent", "Percent"), ("amount", "Amount")],
        readonly=False,
        copy=False,
        help="For each invoice installment, suggested retention amount "
        "to be withheld on payment.\n"
        "Note: as a suggestiong, during payment, user can ignore it.",
    )
    amount_retention = fields.Float(
        string="Retention",
        readonly=False,
        copy=False,
        help="Retention in percent of this invoice, or by amount",
    )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.use_invoice_plan:
            invoice_vals["payment_retention"] = self.payment_retention
            invoice_vals["amount_retention"] = self.amount_retention
        return invoice_vals

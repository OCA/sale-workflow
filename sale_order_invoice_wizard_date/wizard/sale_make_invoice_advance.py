# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    invoice_date = fields.Date()

    def _prepare_invoice_values(self, order, so_lines, accounts):
        values = super()._prepare_invoice_values(order, so_lines, accounts)
        values["invoice_date"] = self.invoice_date
        return values

    def create_invoices(self):
        self = self.with_context(wizard_order_invoice_date=self.invoice_date)
        return super().create_invoices()

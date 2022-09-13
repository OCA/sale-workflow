from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    pdp_per_line = fields.Boolean('Deduct Down Payments per Line')

    def create_invoices(self):
        self = self.with_context(sapi_wizard_id=self.id)
        return super(SaleAdvancePaymentInv, self).create_invoices()

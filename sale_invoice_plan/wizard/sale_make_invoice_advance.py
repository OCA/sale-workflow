# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoices(self, sale_orders):
        invoice = super()._create_invoices(sale_orders)
        for sale in sale_orders:
            if sale.use_invoice_plan:
                plan = self.env["sale.invoice.plan"].search([("sale_id", "=", sale.id)])
                plan.invoice_move_ids += invoice
        return invoice

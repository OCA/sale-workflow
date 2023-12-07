# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoices(self, sale_orders):
        invoice = super()._create_invoices(sale_orders)
        # Link created Invoices to the Invoice Plan Lines
        for sale in sale_orders.filtered(lambda x: x.use_invoice_plan):
            plan = sale.invoice_plan_ids.filtered(lambda x: x.to_invoice)
            plan.invoice_move_ids += invoice
        return invoice

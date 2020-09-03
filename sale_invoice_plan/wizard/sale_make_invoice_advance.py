# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        invoice = super()._create_invoice(order, so_line, amount)
        invoice_plan_id = self._context.get("invoice_plan_id")
        if invoice_plan_id:
            plan = self.env["sale.invoice.plan"].browse(invoice_plan_id)
            plan.invoice_move_ids += invoice
        return invoice

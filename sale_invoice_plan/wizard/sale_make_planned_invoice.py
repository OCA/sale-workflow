# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _name = "sale.make.planned.invoice"
    _description = "Wizard when create invoice by plan"

    def create_invoices_by_plan(self):
        sale = self.env["sale.order"].browse(self._context.get("active_id"))
        sale.ensure_one()
        MakeInvoice = self.env["sale.advance.payment.inv"]
        invoice_plans = (
            self._context.get("all_remain_invoices")
            and sale.invoice_plan_ids.filtered(lambda l: not l.invoiced)
            or sale.invoice_plan_ids.filtered("to_invoice")
        )
        for plan in invoice_plans.sorted("installment"):
            makeinv_wizard = {"advance_payment_method": "delivered"}
            if plan.invoice_type == "advance":
                makeinv_wizard["advance_payment_method"] = "percentage"
                makeinv_wizard["amount"] = plan.percent
            makeinvoice = MakeInvoice.create(makeinv_wizard)
            makeinvoice.sudo().with_context(invoice_plan_id=plan.id).create_invoices()
        return {"type": "ir.actions.act_window_close"}

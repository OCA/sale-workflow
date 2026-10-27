# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleCreateInvoicePlan(models.TransientModel):
    _inherit = "sale.create.invoice.plan"

    # Sequential derives num_installment from the order lines; the field is hidden.
    parent_invoice_plan_method = fields.Selection(
        selection=lambda self: self.env["sale.order"]
        ._fields["invoice_plan_method"]
        .selection,
        string="SO Invoice Plan Method",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get("active_id")
        if not active_id:
            return res
        order = self.env["sale.order"].browse(active_id).exists()
        if not order.use_invoice_plan or not order.invoice_plan_method:
            return res
        method = order.invoice_plan_method
        res["parent_invoice_plan_method"] = method
        if method == "sequential":
            # The derived count replaces any user input before the wizard opens.
            res["num_installment"] = order._get_sequential_num_installment()
        return res

    @api.constrains("num_installment")
    def _check_num_installment(self):
        # Sequential derives num_installment itself; skip the generic >1 check.
        non_sequential = self.filtered(
            lambda rec: rec.parent_invoice_plan_method != "sequential"
        )
        return super(SaleCreateInvoicePlan, non_sequential)._check_num_installment()

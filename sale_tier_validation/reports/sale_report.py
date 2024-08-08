# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class ReportSaleOrder(models.AbstractModel):
    _name = "report.sale.report_saleorder"
    _description = "Sale Order Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["sale.order"].browse(docids)
        for order in docs:
            if not order.company_id.sale_report_print_block:
                continue
            if order.need_validation or (order.review_ids and not order.validated):
                raise UserError(
                    _("Quotation printing is blocked until the order is approved.")
                )
        return {
            "doc_ids": docids,
            "doc_model": "sale.order",
            "docs": docs,
            "data": data,
        }

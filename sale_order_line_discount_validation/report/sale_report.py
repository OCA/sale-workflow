# Copyright (c) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import Warning


class SaleOrderReport(models.AbstractModel):
    _name = "report.sale.report_saleorder"
    _description = "Sale Order Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["sale.order"].browse(docids)
        for rec in docs:
            if rec.order_line.filtered(
                lambda r: r.discount >= rec.env.company.sale_discount_limit
            ) and rec.state not in ("approved", "done"):
                rec._request_approval()
                raise Warning(
                    _(
                        "Your quotation has been sent for approval. You will be "
                        "notified when it is approved or refused."
                    )
                )
        return {"doc_model": "sale.order", "docs": docs}

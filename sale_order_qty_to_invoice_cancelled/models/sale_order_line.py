# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # no trigger product_id.invoice_policy to avoid retroactively changing SO
    @api.depends("qty_invoiced", "order_id.state")
    def _get_to_invoice_qty(self):
        super(SaleOrderLine, self)._get_to_invoice_qty()
        for sol in self:
            if (
                sol.order_id.state == "cancel"
                and sol.product_id.invoice_policy == "order"
            ):
                sol.qty_to_invoice = -sol.qty_invoiced

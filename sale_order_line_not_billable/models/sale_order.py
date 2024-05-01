# Copyright <2022> <Janik von Rotz - Mint System>
# Copyright <2024> <Denis Leemann - Camptocamp SA>
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        # Filter lines with non billable products or that are sections or notes
        invoiceable_lines = super()._get_invoiceable_lines(final=final)
        return invoiceable_lines.filtered(
            lambda line: not line.product_id or line.product_id.billable
        )

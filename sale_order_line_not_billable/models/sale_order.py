from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        """Filter lines with non billable products."""
        invoiceable_lines = super()._get_invoiceable_lines(final=final)
        return invoiceable_lines.filtered(lambda line: line.product_id.billable)

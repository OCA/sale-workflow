# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        if self.env.company.no_product_code_in_sale_line_name:
            self = self.with_context(display_default_code=False)
        return super()._prepare_invoice_line(**optional_values)

# Copyright 2026 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        """
        Override function from sale in order to keep name from sale_order_line
        on invoice line
        """
        res = super()._prepare_invoice_line(**optional_values)
        if res["display_type"] == "product" and res["name"] != self.name:
            res["name"] = self.name
        return res

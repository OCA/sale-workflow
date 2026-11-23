# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["product.name.visibility.mixin", "sale.order.line"]

    def _prepare_invoice_line(self, **optional_values):
        # Propagate hide_product_name from sale order lines to invoice lines
        vals = super()._prepare_invoice_line(**optional_values)
        if vals.get("display_type") == "product":
            vals.setdefault("hide_product_name", self.hide_product_name)
        return vals
